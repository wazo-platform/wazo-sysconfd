# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from optparse import OptionParser
from xivo import http_json_server
from xivo.daemonize import pidfile_context
from xivo.http_json_server import CMD_R
from xivo.xivo_logging import setup_logging
from xivo_sysconf.modules import *
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


def get_log_level_by_name(loglevel_name):
    levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'WARN': logging.WARN,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
    }
    loglevel_name = loglevel_name.upper()
    if loglevel_name in levels:
        return levels[loglevel_name]
    else:
        raise ValueError("Unknown log level %r" % loglevel_name)


def argv_parse_check():
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-l",
                      dest='loglevel',
                      default='info',
                      help="Emit traces with LOGLEVEL details, must be one of:\n"
                           "critical, error, warning, info, debug")
    parser.add_option("-f",
                      action='store_true',
                      dest='foreground',
                      default=False,
                      help="Foreground, don't daemonize")
    parser.add_option("-c",
                      dest='conffile',
                      default="/etc/xivo/sysconfd.conf",
                      help="Use configuration file <conffile> instead of %default")
    parser.add_option("-p",
                      dest='pidfile',
                      default="/var/run/xivo-sysconfd.pid",
                      help="Use PID file <pidfile> instead of %default")
    parser.add_option("--listen-addr",
                      dest='listen_addr',
                      default='127.0.0.1',
                      help="Listen on address <listen_addr> instead of %default")
    parser.add_option("--listen-port",
                      dest='listen_port',
                      type='int',
                      default=8668,
                      help="Listen on port <listen_port> instead of %default")

    options, args = parser.parse_args()

    if args:
        parser.error("no argument is allowed - use option --help to get an help screen")

    try:
        num_loglevel = get_log_level_by_name(options.loglevel)
    except ValueError:
        parser.error("incorrect log level %r" % options.loglevel)
    options.loglevel = num_loglevel

    return options


def status_check(args, options):
    return {'status': 'up'}


def main():
    "entry point"
    http_json_server.register(status_check, CMD_R, name='status-check')
    options = argv_parse_check()

    setup_logging(LOG_FILE_NAME, options.foreground, debug=(options.loglevel == logging.DEBUG))

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
