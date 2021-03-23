# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy


_DEFAULT_CONFIG = {
    'config_file': '/etc/wazo-sysconfd/config.yml',
    'extra_config_files': '/etc/wazo-sysconfd/conf.d/',
    'xivo_config_path': '/etc/xivo',
    'templates_path': '/usr/share/wazo-sysconfd/templates',
    'custom_templates_path': '/etc/xivo/sysconfd/custom-templates',
    'backup_path': '/var/backups/wazo-sysconfd',
    'resolvconf': {
        'hostname_file': '/etc/hostname',
        'hosts_file': '/etc/hosts',
        'resolvconf_file': '/etc/resolv.conf',
    },
    'network': {
        'interfaces_file': '/etc/network/interfaces',
    },
    'wizard': {
        'templates_path': '/usr/share/xivo-config/templates',
        'custom_templates_path': '/etc/xivo/custom-templates',
    },
    'commonconf': {
        'commonconf_file': '/etc/xivo/common.conf',
        'commonconf_generate_cmd': '/usr/sbin/xivo-create-config',
        'commonconf_update_cmd': '/usr/sbin/xivo-update-config',
        'commonconf_monit': '/usr/sbin/xivo-monitoring-update',
    },
    'monit': {
        'monit_checks_dir': '/usr/share/xivo-monitoring/checks',
        'monit_conf_dir': '/etc/monit/conf.d',
    },
    'request_handlers': {
        'synchronous': False,
    },
    'bus': {
        'username': 'guest',
        'password': 'guest',
        'host': 'localhost',
        'port': 5672,
        'exchange_name': 'xivo',
        'exchange_type': 'topic',
        'exchange_durable': True,
    },
}


def load_config():
    file_config = read_config_file_hierarchy(_DEFAULT_CONFIG)
    return ChainMap(file_config, _DEFAULT_CONFIG)
