# Copyright 2012-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
import json
import os.path
import shutil
import subprocess
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

from wazo_sysconfd.plugins.ha_config.ha import (
    HAConfigManager,
    _CronFileInstaller,
    _PostgresConfigUpdater,
    _SentinelFileManager,
)


def new_master_ha_config(slave_ip_address):
    return _new_ha_config('master', slave_ip_address)


def new_slave_ha_config(master_ip_address):
    return _new_ha_config('slave', master_ip_address)


def new_disabled_ha_config():
    return _new_ha_config('disabled', '')


def _new_ha_config(node_type, remote_address):
    return {'node_type': node_type, 'remote_address': remote_address}


def mock_subprocess_check_call(f):
    @functools.wraps(f)
    def decorator(*kargs):
        old_subprocess_check_call = subprocess.check_call
        subprocess.check_call = Mock()

        try:
            f(*kargs)
        finally:
            subprocess.check_call = old_subprocess_check_call

    return decorator


class TestHA(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self._ha_conf_file = os.path.join(self._tmp_dir, 'test_ha.conf')
        self._ha_config_mgr = HAConfigManager(
            Mock(), Mock(), Mock(), ha_conf_file=self._ha_conf_file
        )

    def tearDown(self):
        shutil.rmtree(self._tmp_dir)

    def _create_tmp_conf_file(self, content):
        with open(self._ha_conf_file, 'w') as fobj:
            fobj.write(content)

    def test_read_conf(self):
        content = """\
{
    "node_type" : "master",
    "remote_address" : "10.0.0.1"
}
"""
        expected_ha_config = new_master_ha_config('10.0.0.1')
        fobj = StringIO(content)

        ha_config = self._ha_config_mgr._read_ha_config_from_fobj(fobj)

        self.assertEqual(expected_ha_config, ha_config)

    def test_write_conf(self):
        ha_config = new_master_ha_config('10.0.0.1')
        expected_content = '{"node_type": "master", "remote_address": "10.0.0.1"}'
        fobj = StringIO()

        self._ha_config_mgr._write_ha_config_to_fobj(ha_config, fobj)

        content = fobj.getvalue()
        self.assertEqual(json.loads(expected_content), json.loads(content))

    def test_get_ha_config_no_file(self):
        expected_ha_config = new_disabled_ha_config()

        ha_config = self._ha_config_mgr.get_ha_config(None, None)

        self.assertEqual(expected_ha_config, ha_config)

    def test_get_ha_config(self):
        content = """\
{
    "node_type" : "master",
    "remote_address" : "10.0.0.1"
}
"""
        expected_ha_config = new_master_ha_config('10.0.0.1')
        self._create_tmp_conf_file(content)

        ha_config = self._ha_config_mgr.get_ha_config(None, None)

        self.assertEqual(expected_ha_config, ha_config)

    def test_update_ha_config(self):
        ha_config = new_master_ha_config('10.0.0.1')
        self._ha_config_mgr._manage_services = Mock()

        self._ha_config_mgr.update_ha_config(ha_config, None)

        expected_ha_config = self._ha_config_mgr._read_ha_config()
        self.assertEqual(expected_ha_config, ha_config)

    @mock_subprocess_check_call
    def test_manage_services_disabled(self):
        ha_config = new_disabled_ha_config()

        self._ha_config_mgr._manage_services(ha_config)

        subprocess.check_call.assert_called_with(
            ['/usr/sbin/xivo-manage-slave-services', 'start'], close_fds=True
        )

    @mock_subprocess_check_call
    def test_manage_services_master(self):
        ha_config = new_master_ha_config('10.0.0.1')

        self._ha_config_mgr._manage_services(ha_config)

        subprocess.check_call.assert_called_with(
            ['/usr/sbin/xivo-manage-slave-services', 'start'], close_fds=True
        )

    @mock_subprocess_check_call
    def test_manage_services_slave(self):
        ha_config = new_slave_ha_config('10.0.0.1')

        self._ha_config_mgr._manage_services(ha_config)

        self.assertFalse(subprocess.check_call.called)


class TestPostgresConfigUpdater(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self._pg_hba_filename = os.path.join(
            self._tmp_dir, _PostgresConfigUpdater.PG_HBA_FILE
        )
        self._postgresql_filename = os.path.join(
            self._tmp_dir, _PostgresConfigUpdater.POSTGRESQL_FILE
        )

    def tearDown(self):
        shutil.rmtree(self._tmp_dir)

    def test_update_pg_hba_file_from_non_slave_to_slave(self):
        pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
"""
        expected_pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
host asterisk postgres 10.0.0.1/32 trust
"""
        self._write_pg_hba_file(pg_hba_content)
        ha_config = new_slave_ha_config('10.0.0.1')
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_pg_hba_file()

        self.assertEqual(expected_pg_hba_content, self._read_pg_hba_file())

    def _new_postgres_updater(self, ha_config):
        return _PostgresConfigUpdater(ha_config, self._tmp_dir)

    def _write_pg_hba_file(self, content):
        self._write_file(self._pg_hba_filename, content)

    def _write_postgresql_file(self, content):
        self._write_file(self._postgresql_filename, content)

    def _write_file(self, filename, content):
        with open(filename, 'w') as fobj:
            fobj.write(content)

    def _read_pg_hba_file(self):
        return self._read_file(self._pg_hba_filename)

    def _read_postgresql_file(self):
        return self._read_file(self._postgresql_filename)

    def _read_file(self, filename):
        with open(filename) as fobj:
            return fobj.read()

    def test_update_pg_hba_file_from_slave_to_slave(self):
        pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
host asterisk postgres 10.0.0.1/32 trust
"""
        expected_pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
host asterisk postgres 10.0.0.2/32 trust
"""
        self._write_pg_hba_file(pg_hba_content)
        ha_config = new_slave_ha_config('10.0.0.2')
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_pg_hba_file()

        self.assertEqual(expected_pg_hba_content, self._read_pg_hba_file())

    def test_update_pg_hba_file_from_slave_to_non_slave(self):
        pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
host asterisk postgres 10.0.0.1/32 trust
"""
        expected_pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
"""
        self._write_pg_hba_file(pg_hba_content)
        ha_config = new_disabled_ha_config()
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_pg_hba_file()

        self.assertEqual(expected_pg_hba_content, self._read_pg_hba_file())

    def test_update_postgresql_file_from_non_slave_to_slave(self):
        postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
"""
        expected_postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
listen_addresses = '*'
"""
        self._write_postgresql_file(postgresql_content)
        ha_config = new_slave_ha_config('10.0.0.1')
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_postgresql_file()

        self.assertEqual(expected_postgresql_content, self._read_postgresql_file())

    def test_update_postgresql_file_from_slave_to_slave(self):
        postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
listen_addresses = '*'
"""
        expected_postgresql_content = postgresql_content
        self._write_postgresql_file(postgresql_content)
        ha_config = new_slave_ha_config('10.0.0.1')
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_postgresql_file()

        self.assertEqual(expected_postgresql_content, self._read_postgresql_file())

    def test_update_postgresql_file_from_slave_to_non_slave(self):
        postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
listen_addresses = '*'
"""
        expected_postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
"""
        self._write_postgresql_file(postgresql_content)
        ha_config = new_disabled_ha_config()
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_postgresql_file()

        self.assertEqual(expected_postgresql_content, self._read_postgresql_file())


class TestCronFileInstaller(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmp_dir)

    def test_add_cronfile(self):
        filename = 'test-cronfile'
        content = 'foo bar\n'
        cronfile_installer = self._new_cronfile_installer()

        cronfile_installer.add_cronfile(filename, content)

        self.assertEqual(content, self._read_cronfile(filename))

    def _new_cronfile_installer(self):
        return _CronFileInstaller(self._tmp_dir)

    def _read_cronfile(self, filename):
        abs_filename = os.path.join(self._tmp_dir, filename)
        with open(abs_filename) as fobj:
            return fobj.read()

    def test_remove_cronfile_when_cronfile_present(self):
        filename = 'test-cronfile'
        cronfile_installer = self._new_cronfile_installer()
        cronfile_installer.add_cronfile(filename, '')

        cronfile_installer.remove_cronfile(filename)

        self.assertEqual([], self._list_crondir())

    def _list_crondir(self):
        return os.listdir(self._tmp_dir)

    def test_remove_cronfile_when_cronfile_absent(self):
        filename = 'test-cronfile'
        cronfile_installer = self._new_cronfile_installer()

        cronfile_installer.remove_cronfile(filename)

        self.assertEqual([], self._list_crondir())


class TestSentinelFilesManager(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(tempfile.mkdtemp())
        self.sentinel_file_manager = _SentinelFileManager(self.root_dir)

    def tearDown(self):
        shutil.rmtree(self.root_dir)

    def test_primary(self):
        ha_config = new_master_ha_config('10.0.0.1')
        self.sentinel_file_manager.install(ha_config)
        sentinel_file = self.root_dir / 'is-primary'
        self.assertTrue(sentinel_file.exists())
        anti_sentinel_file = self.root_dir / 'is-secondary'
        self.assertFalse(anti_sentinel_file.exists())

    def test_secondary(self):
        ha_config = new_slave_ha_config('10.0.0.2')
        self.sentinel_file_manager.install(ha_config)
        sentinel_file = self.root_dir / 'is-secondary'
        self.assertTrue(sentinel_file.exists())
        anti_sentinel_file = self.root_dir / 'is-primary'
        self.assertFalse(anti_sentinel_file.exists())

    def test_disabled(self):
        ha_config = new_disabled_ha_config()
        self.sentinel_file_manager.install(ha_config)
        primary_sentinel_file = self.root_dir / 'is-primary'
        secondary_sentinel_file = self.root_dir / 'is-secondary'
        self.assertFalse(primary_sentinel_file.exists())
        self.assertFalse(secondary_sentinel_file.exists())
