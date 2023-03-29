# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import errno
import json
import os
import subprocess
from pathlib import Path
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    SECONDARY = 'slave'
    PRIMARY = 'master'
    DISABLED = 'disabled'


class HAConfigManager(object):
    DEFAULT_HA_CONF_FILE = '/etc/xivo/ha.conf'
    DEFAULT_HA_CONFIG = {'node_type': 'disabled', 'remote_address': ''}
    CRONFILE_SLAVE = 'xivo-ha-slave'
    CRONFILE_MASTER = 'xivo-ha-master'

    def __init__(
        self,
        postgres_config_updater_factory,
        cronfile_installer,
        sentinel_file_manager,
        ha_conf_file=DEFAULT_HA_CONF_FILE,
    ):
        self._postgres_config_updater_factory = postgres_config_updater_factory
        self._cronfile_installer = cronfile_installer
        self._sentinel_file_manager = sentinel_file_manager
        self._ha_conf_file = ha_conf_file

    def get_ha_config(self, args, options):
        return self._read_ha_config()

    def _read_ha_config(self):
        try:
            with open(self._ha_conf_file, 'r') as fobj:
                return self._read_ha_config_from_fobj(fobj)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return dict(self.DEFAULT_HA_CONFIG)
            else:
                raise

    def _read_ha_config_from_fobj(self, fobj):
        return json.load(fobj)

    def update_ha_config(self, args, options):
        ha_config = args
        self._write_ha_config(ha_config)
        self._update_postgres(ha_config)
        self._update_cronfiles(ha_config)
        self._manage_services(ha_config)
        self._manage_sentinel_files(ha_config)

    def _write_ha_config(self, ha_config):
        with open(self._ha_conf_file, 'w') as fobj:
            self._write_ha_config_to_fobj(ha_config, fobj)

    def _write_ha_config_to_fobj(self, ha_config, fobj):
        json.dump(ha_config, fobj)

    def _update_postgres(self, ha_config):
        postgres_updater = self._postgres_config_updater_factory(ha_config)
        postgres_updater.update_pg_hba_file()
        postgres_updater.update_postgresql_file()
        postgres_updater.restart_postgres()

    def _update_cronfiles(self, ha_config):
        node_type = ha_config['node_type']
        remote_address = ha_config['remote_address']
        self._cronfile_installer.remove_cronfile(self.CRONFILE_MASTER)
        self._cronfile_installer.remove_cronfile(self.CRONFILE_SLAVE)
        if node_type == 'master':
            self._add_master_cronfile(remote_address)
        elif node_type == 'slave':
            self._add_slave_cronfile(remote_address)

    def _add_master_cronfile(self, remote_address):
        content = (
            '0 * * * * root /usr/sbin/xivo-master-slave-db-replication %s >/dev/null\n'
            '0 * * * * root /usr/bin/xivo-sync >/dev/null\n' % remote_address
        )
        self._cronfile_installer.add_cronfile(self.CRONFILE_MASTER, content)

    def _add_slave_cronfile(self, remote_address):
        content = (
            '* * * * * root /usr/sbin/xivo-check-master-status %s >/dev/null\n'
            % remote_address
        )
        self._cronfile_installer.add_cronfile(self.CRONFILE_SLAVE, content)

    def _manage_services(self, ha_config):
        if ha_config['node_type'] != 'slave':
            command_args = ['/usr/sbin/xivo-manage-slave-services', 'start']
            subprocess.check_call(command_args, close_fds=True)

    def _manage_sentinel_files(self, ha_config):
        self._sentinel_file_manager.install(ha_config)


class _PostgresConfigUpdater(object):
    DEFAULT_CONFIG_DIR = '/etc/postgresql/11/main'
    PG_HBA_FILE = 'pg_hba.conf'
    POSTGRESQL_FILE = 'postgresql.conf'

    def __init__(self, ha_config, postgres_config_dir=DEFAULT_CONFIG_DIR):
        self._ha_config = ha_config
        self._pg_hba_file = os.path.join(postgres_config_dir, self.PG_HBA_FILE)
        self._postgresql_file = os.path.join(postgres_config_dir, self.POSTGRESQL_FILE)

    def update_pg_hba_file(self):
        self._clear_host_line_in_pg_hba()
        if self._ha_config['node_type'] == 'slave':
            self._append_host_line_in_pg_hba()

    def _clear_host_line_in_pg_hba(self):
        command_args = ['sed', '-i', '/^host asterisk postgres/d', self._pg_hba_file]
        subprocess.check_call(command_args, close_fds=True)

    def _append_host_line_in_pg_hba(self):
        master_ip_address = self._ha_config['remote_address']
        host_line = 'host asterisk postgres %s/32 trust\n' % master_ip_address
        with open(self._pg_hba_file, 'a') as fobj:
            fobj.write(host_line)

    def update_postgresql_file(self):
        self._clear_listen_addresses_line_in_postgresql()
        if self._ha_config['node_type'] == 'slave':
            self._append_listen_addresses_line_in_postgresql()

    def _clear_listen_addresses_line_in_postgresql(self):
        command_args = ['sed', '-i', '/^listen_addresses/d', self._postgresql_file]
        subprocess.check_call(command_args, close_fds=True)

    def _append_listen_addresses_line_in_postgresql(self):
        listen_addresses_line = "listen_addresses = '*'\n"
        with open(self._postgresql_file, 'a') as fobj:
            fobj.write(listen_addresses_line)

    def restart_postgres(self):
        command_args = ['/bin/systemctl', 'restart', 'postgresql.service']
        subprocess.check_call(command_args, close_fds=True)


class _CronFileInstaller(object):
    DEFAULT_CRON_DIR = '/etc/cron.d'

    def __init__(self, cron_dir=DEFAULT_CRON_DIR):
        self._cron_dir = cron_dir

    def add_cronfile(self, filename, content):
        abs_filename = os.path.join(self._cron_dir, filename)
        with open(abs_filename, 'w') as fobj:
            fobj.write(content)

    def remove_cronfile(self, filename):
        abs_filename = os.path.join(self._cron_dir, filename)
        try:
            os.unlink(abs_filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise


class _SentinelFileManager:
    SENTINEL_ROOT_DIR = Path('/var/lib/wazo')
    PRIMARY_SENTINEL_NAME = 'is-primary'
    SECONDARY_SENTINEL_NAME = 'is-secondary'

    def __init__(self, root_dir: os.PathLike = SENTINEL_ROOT_DIR):
        self._root_dir = Path(root_dir)
        self._primary_sentinel = self._root_dir / self.PRIMARY_SENTINEL_NAME
        self._secondary_sentinel = self._root_dir / self.SECONDARY_SENTINEL_NAME

    def _install_primary(self):
        if self._secondary_sentinel.exists():
            self._secondary_sentinel.unlink()
        sentinel = self._primary_sentinel
        logger.info('Creating primary sentinel file %s.', sentinel)
        sentinel.touch()

    def _install_secondary(self):
        if self._primary_sentinel.exists():
            self._primary_sentinel.unlink()
        sentinel = self._secondary_sentinel
        logger.info('Creating secondary sentinel file %s.', sentinel)
        sentinel.touch()

    def install(self, ha_config: dict):
        mode = NodeType(ha_config['node_type'])
        if mode is NodeType.SECONDARY:
            logger.info('Node is in secondary HA mode.')
            self._install_secondary()
        elif mode is NodeType.PRIMARY:
            logger.info('Node is in primary HA mode.')
            self._install_primary()
        elif mode is NodeType.DISABLED:
            logger.info('HA disabled on this node.')
            self.uninstall(ha_config)

    def uninstall(self, ha_config: dict):
        logger.info('Removing sentinel files.')
        if self._primary_sentinel.exists():
            self._primary_sentinel.unlink()
        if self._secondary_sentinel.exists():
            self._secondary_sentinel.unlink()
