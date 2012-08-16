# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2012  Avencall

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""

import ConfigParser
import logging
import subprocess
import socket

from xivo.http_json_server import register, HttpReqError, CMD_RW

from pprint import pprint


logger = logging.getLogger(__name__)

SOCKET_CONFFILE = '/etc/pf-xivo/sysconfd/socket.conf'

AST_CMDS = [
    'core reload',
    'core restart now',
    'core show version',
    'core show channels',
    'dialplan reload',
    'sccp reload',
    'sip reload',
    'moh reload',
    'iax2 reload',
    'module reload',
    'module reload app_queue.so',
    'module reload chan_agent.so',
    'module reload app_meetme.so',
    'features reload',
    'voicemail reload',
    'module reload chan_sccp.so',
    'sccp show version',
    'sccp show devices',
    'sccp show config',
    'sccp update config',
    ]

class RequestHandlers(object):

    def __init__(self):
        conf_obj = ConfigParser.RawConfigParser()
        conf_obj.readfp(open(SOCKET_CONFFILE))

        self.ctibus_host = conf_obj.get('ctibus', 'bindaddr')
        self.ctibus_port = int(conf_obj.get('ctibus', 'port'))

        self.dirdbus_host = conf_obj.get('dirdbus', 'bindaddr')
        self.dirdbus_port = int(conf_obj.get('dirdbus', 'port'))

    def _exec_ast_cmd(self, cmds):
        logger.debug('-----------------------ASTERISK--------------------------')
        logger.debug(cmds)
        ret = []
        for cmd in cmds:
            if cmd in AST_CMDS or cmd.startswith('sip show peer'):
                try:
                    p = subprocess.Popen(['asterisk', '-rx', cmd],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        close_fds=True)
                    output = p.communicate()[0]

                    if p.returncode != 0:
                        raise HttpReqError(500, output)
                    else:
                        logger.info("Asterisk command '%s' successfully executed", cmd)
                except OSError:
                    logger.exception("Error while executing asterisk command")
                    raise HttpReqError(500, "can't manage exec_cmd_asterisk")
                ret.append(output)
            else:
                logger.error("cmd %s not authorized on", cmd)
        return ret

    def _exec_ctibus_cmd(self, cmds):
        logger.debug('-----------------------CTIBUS--------------------------')
        logger.debug(cmds)
        ret = []
        for cmd in cmds:
            socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_obj.connect((self.ctibus_host, self.ctibus_port))
            socket_obj.send(cmd)
            data = socket_obj.recv(1024)
            ret.append(data)
            socket_obj.close()
        return ret

    def _exec_dird_cmd(self, cmds):
        logger.debug('-----------------------DIRDBUS--------------------------')
        logger.debug(cmds)
        for cmd in cmds:
            socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_obj.connect((self.dirdbus_host, self.dirdbus_port))
            socket_obj.send(cmd)
            socket_obj.close()
        

    def process(self, args, options):
        for kind in args.keys():
            if kind not in ['ipbx', 'ctibus', 'dird']:
                raise HttpReqError(500, "Error wrong data received")

        ret = {}
        ret['ipbx'] = self._exec_ast_cmd(args['ipbx'])
        self._exec_ctibus_cmd(args['ctibus'])
        self._exec_dird_cmd(args['dird'])
        logger.debug(ret)
        return ret

request_handlers = RequestHandlers()
register(request_handlers.process, CMD_RW, name='exec_request_handlers')
