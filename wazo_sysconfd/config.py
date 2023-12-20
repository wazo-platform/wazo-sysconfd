# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from collections import namedtuple

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy
from xivo.xivo_logging import get_log_level_by_name

_DEFAULT_CONFIG = {
    'config_file': '/etc/wazo-sysconfd/config.yml',
    'extra_config_files': '/etc/wazo-sysconfd/conf.d/',
    'xivo_config_path': '/etc/xivo',
    'templates_path': '/usr/share/wazo-sysconfd/templates',
    'custom_templates_path': '/etc/xivo/sysconfd/custom-templates',
    'backup_path': '/var/backups/wazo-sysconfd',
    'debug': True,
    'log_level': 'info',
    'log_file': '/var/log/wazo-sysconfd.log',
    'rest_api': {
        'listen': '127.0.0.1',
        'port': 8668,
    },
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
        'exchange_name': 'wazo-headers',
        'exchange_type': 'headers',
    },
    'enabled_plugins': {
        'asterisk': True,
        'commonconf': True,
        'dhcp_update': True,
        'ha_config': True,
        'host_services': True,
        'hosts': True,
        'request_handlers': True,
        'resolv_conf': True,
        'status': True,
        'xivoctl': True,
        'networking_info': True,
    },
}


def _get_reinterpreted_raw_values(*configs):
    config = ChainMap(*configs)
    log_level_name = 'debug' if config['debug'] else config['log_level']
    return {'log_level': get_log_level_by_name(log_level_name)}


def _parse_cli_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--config-file',
        default="/etc/wazo-sysconfd/config.yml",
        help="Use configuration file <config-file> instead of %(default)s",
    )
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='Log debug mesages. Override log_level',
    )
    parser.add_argument(
        '--listen-addr', help="Listen on address <listen_addr> instead of 127.0.0.1"
    )
    parser.add_argument(
        '--listen-port', type=int, help="Listen on port <listen_port> instead of 8668"
    )

    parsed_args = parser.parse_args(argv)
    result = {'rest_api': {}}
    if parsed_args.debug:
        result['debug'] = parsed_args.debug
    if parsed_args.config_file:
        result['config_file'] = parsed_args.config_file
    if parsed_args.listen_addr:
        result['rest_api']['listen'] = parsed_args.listen_addr
    if parsed_args.listen_port:
        result['rest_api']['port'] = parsed_args.listen_port
    return result


def load_config(argv):
    cli_config = _parse_cli_args(argv)
    file_config = read_config_file_hierarchy(ChainMap(cli_config, _DEFAULT_CONFIG))
    reinterpreted_config = _get_reinterpreted_raw_values(
        cli_config, file_config, _DEFAULT_CONFIG
    )
    return ChainMap(reinterpreted_config, cli_config, file_config, _DEFAULT_CONFIG)


def prepare_http_server_options(configuration):
    HTTPServerOptions = namedtuple(
        'HTTPServerOptions', ['listen_addr', 'listen_port', 'configuration']
    )
    return HTTPServerOptions(
        configuration['rest_api']['listen'],
        configuration['rest_api']['port'],
        configuration,
    )
