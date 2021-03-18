# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging
import os
from ConfigParser import ConfigParser
from StringIO import StringIO

from xivo import http_json_server
from xivo.http_json_server import CMD_R
from xivo.xivo_logging import setup_logging, get_log_level_by_name

from xivo_sysconf.modules import *

LOG_FILE_NAME = "/var/log/wazo-sysconfd.log"

log = logging.getLogger('wazo-sysconfd')

SysconfDefaultsConf = StringIO("""
[general]
xivo_config_path        = /etc/xivo
templates_path          = /usr/share/wazo-sysconfd/templates
custom_templates_path   = /etc/xivo/sysconfd/custom-templates
backup_path             = /var/backups/wazo-sysconfd
""")


def argv_parse_check():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l',
                        '--loglevel',
                        type=get_log_level_by_name,
                        default='info',
                        help="Emit traces with LOGLEVEL details, must be one of:\n"
                             "critical, error, warning, info, debug")
    parser.add_argument('-c',
                        '--conffile',
                        default="/etc/xivo/sysconfd.conf",
                        help="Use configuration file <conffile> instead of %(default)s")
    parser.add_argument('--listen-addr',
                        default='127.0.0.1',
                        help="Listen on address <listen_addr> instead of %(default)s")
    parser.add_argument('--listen-port',
                        type=int,
                        default=8668,
                        help="Listen on port <listen_port> instead of %(default)s")

    return parser.parse_args()


def status_check(args, options):
    return {'status': 'up'}


def main():
    "entry point"
    http_json_server.register(status_check, CMD_R, name='status-check')
    options = argv_parse_check()

    setup_logging(LOG_FILE_NAME, log_level=options.loglevel)

    cp = ConfigParser()
    cp.readfp(SysconfDefaultsConf)
    cp.readfp(open(options.conffile))

    options.configuration = cp

    http_json_server.init(options)

    try:
        os.umask(022)
        http_json_server.run(options)
    except SystemExit:
        raise
    except Exception:
        log.exception("bad things happen")


if __name__ == '__main__':
    main()
