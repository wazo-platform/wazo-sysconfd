# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from ConfigParser import ConfigParser
from StringIO import StringIO
from xivo import http_json_server
from xivo.daemonize import pidfile_context
from xivo.http_json_server import CMD_R
from xivo.xivo_logging import setup_logging, get_log_level_by_name
from xivo_sysconf.modules import *
import argparse
import logging
import os


LOG_FILE_NAME = "/var/log/xivo-sysconfd.log"

log = logging.getLogger('xivo-sysconfd')

SysconfDefaultsConf = StringIO("""
[general]
xivo_config_path        = /etc/xivo
templates_path          = /usr/share/xivo-sysconfd/templates
custom_templates_path   = /etc/xivo/sysconfd/custom-templates
backup_path             = /var/backups/xivo-sysconfd
""")


def argv_parse_check():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l',
                        '--loglevel',
                        type=get_log_level_by_name,
                        default='info',
                        help="Emit traces with LOGLEVEL details, must be one of:\n"
                             "critical, error, warning, info, debug")
    parser.add_argument('-f',
                        '--foreground',
                        action='store_true',
                        help="Foreground, don't daemonize")
    parser.add_argument('-c',
                        '--conffile',
                        default="/etc/xivo/sysconfd.conf",
                        help="Use configuration file <conffile> instead of %(default)s")
    parser.add_argument('-p',
                        '--pidfile',
                        default="/var/run/xivo-sysconfd.pid",
                        help="Use PID file <pidfile> instead of %(default)s")
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

    setup_logging(LOG_FILE_NAME, options.foreground, log_level=options.loglevel)

    cp = ConfigParser()
    cp.readfp(SysconfDefaultsConf)
    cp.readfp(open(options.conffile))

    options.configuration = cp

    http_json_server.init(options)

    with pidfile_context(options.pidfile, options.foreground):
        try:
            os.umask(022)
            http_json_server.run(options)
        except SystemExit:
            raise
        except Exception:
            log.exception("bad things happen")


if __name__ == '__main__':
    main()
