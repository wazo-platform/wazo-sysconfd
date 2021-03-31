# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
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
    'log_file': '/var/log/wazo-sysconfd.log',
    'log_level': 'info',
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
        'exchange_name': 'xivo',
        'exchange_type': 'topic',
        'exchange_durable': True,
    },
}


def _get_reinterpreted_raw_values(config):
    result = {}

    log_level = config.get('log_level')
    if log_level:
        result['log_level'] = get_log_level_by_name(log_level)

    return result


def _parse_cli_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-l',
                        '--log-level',
                        type=get_log_level_by_name,
                        help="Emit traces with LOGLEVEL details, must be one of:\n"
                             "critical, error, warning, info, debug")
    parser.add_argument('-c',
                        '--config-file',
                        default="/etc/wazo-sysconfd/config.yml",
                        help="Use configuration file <config-file> instead of %(default)s")
    parser.add_argument('--listen-addr',
                        default='127.0.0.1',
                        help="Listen on address <listen_addr> instead of %(default)s")
    parser.add_argument('--listen-port',
                        type=int,
                        default=8668,
                        help="Listen on port <listen_port> instead of %(default)s")

    parsed_args = parser.parse_args(argv)
    result = {}
    if parsed_args.log_level:
        result['log_level'] = parsed_args.log_level
    if parsed_args.config_file:
        result['config_file'] = parsed_args.config_file
    if parsed_args.listen_addr:
        result['listen_addr'] = parsed_args.listen_addr
    if parsed_args.listen_port:
        result['listen_port'] = parsed_args.listen_port
    return result


def load_config(argv):
    cli_config = _parse_cli_args(argv)
    file_config = read_config_file_hierarchy(ChainMap(cli_config, _DEFAULT_CONFIG))
    intermediate_config = ChainMap(cli_config, file_config, _DEFAULT_CONFIG)
    return _get_reinterpreted_raw_values(intermediate_config)


def prepare_http_server_options(configuration):
    configuration['configuration'] = configuration
    configuration['listen_addr'] = configuration['rest_api']['listen']
    configuration['listen_port'] = configuration['rest_api']['port']
    HTTPServerOptions = namedtuple('HTTPServerOptions', configuration)
    return HTTPServerOptions(**configuration)
