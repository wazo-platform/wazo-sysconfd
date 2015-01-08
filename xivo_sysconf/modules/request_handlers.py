# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

import ConfigParser
import logging
import subprocess
import socket

from xivo import debug
from xivo.http_json_server import register, HttpReqError, CMD_RW
from xivo_sysconf.modules.agentbus_handler import AgentBusHandler
from xivo_bus.ctl.config import BusConfig
from xivo_bus.resources.agent.client import AgentClient

logger = logging.getLogger(__name__)

SOCKET_CONFFILE = '/etc/xivo/sysconfd/socket.conf'
AST_CMDS = [
    'core reload',
    'core restart now',
    'core show version',
    'core show channels',
    'dialplan reload',
    'sip reload',
    'moh reload',
    'iax2 reload',
    'module reload',
    'module reload app_queue.so',
    'module reload app_meetme.so',
    'features reload',
    'voicemail reload',
    'module reload chan_sccp.so',
    'sccp show version',
    'sccp show devices',
    'sccp show config',
]
AST_ARG_CMDS = [
    'sip show peer',
    'sccp reset',
]


class RequestHandlers(object):

    def __init__(self, agent_bus_handler):
        self._agent_bus_handler = agent_bus_handler

    def read_config(self):
        conf_obj = ConfigParser.RawConfigParser()
        with open(SOCKET_CONFFILE) as fobj:
            conf_obj.readfp(fobj)

        self.ctibus_host = conf_obj.get('ctibus', 'bindaddr')
        self.ctibus_port = int(conf_obj.get('ctibus', 'port'))

        self.dirdbus_host = conf_obj.get('dirdbus', 'bindaddr')
        self.dirdbus_port = int(conf_obj.get('dirdbus', 'port'))

    @debug.trace_duration
    def _exec_ast_cmd(self, cmds):
        logger.debug('-----------------------ASTERISK--------------------------')
        logger.debug(cmds)
        ret = []
        for cmd in cmds:
            if self._is_ast_cmd(cmd):
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

    def _is_ast_cmd(self, cmd):
        if cmd in AST_CMDS:
            return True
        else:
            for ast_arg_cmd in AST_ARG_CMDS:
                if cmd.startswith(ast_arg_cmd):
                    return True
        return False

    @debug.trace_duration
    def _exec_ctibus_cmd(self, cmds):
        logger.debug('-----------------------CTIBUS--------------------------')
        logger.debug(cmds)
        for cmd in cmds:
            try:
                socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_obj.connect((self.ctibus_host, self.ctibus_port))
                socket_obj.send(cmd)
                socket_obj.close()
            except Exception:
                logger.exception("Error while executing CTI command: %s", cmd)
            else:
                logger.info("CTI command '%s' successfully executed", cmd)

    @debug.trace_duration
    def _exec_dird_cmd(self, cmds):
        logger.debug('-----------------------DIRDBUS--------------------------')
        logger.debug(cmds)
        for cmd in cmds:
            try:
                socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                socket_obj.connect((self.dirdbus_host, self.dirdbus_port))
                socket_obj.send(cmd)
                socket_obj.close()
            except Exception:
                logger.exception("Error while executing DIRD command: %s", cmd)
            else:
                logger.info("DIRD command '%s' successfully executed", cmd)

    @debug.trace_duration
    def _exec_agentbus_cmd(self, cmds):
        for cmd in cmds:
            try:
                self._agent_bus_handler.handle_command(cmd)
            except Exception:
                logger.exception("Error wile executing AGENTBUS command: %s", cmd)
            else:
                logger.info("AGENTBUS command '%s' successfully executed", cmd)

    @debug.trace_duration
    def process(self, args, options):
        for kind in args.keys():
            if kind not in ['ipbx', 'ctibus', 'dird', 'agentbus']:
                raise HttpReqError(500, 'Error wrong data received')

        ret = {}
        ret['ipbx'] = self._exec_ast_cmd(args['ipbx'])
        self._exec_ctibus_cmd(args['ctibus'])
        self._exec_dird_cmd(args['dird'])
        self._exec_agentbus_cmd(args.get('agentbus', []))
        logger.debug(ret)
        return ret


class RequestHandlersProxy(object):

    def __init__(self):
        self._initialized = False

    def handle_request(self, args, options):
        if not self._initialized:
            self._initialize()
            self._initialized = True
        return self._request_handlers.process(args, options)

    def _initialize(self):
        logger.info('initializing request handlers')
        self._request_handlers = self._new_request_handlers()
        self._request_handlers.read_config()

    def _new_request_handlers(self):
        agent_client = AgentClient(fetch_response=False, config=self.bus_config)
        agent_client.connect()
        agent_bus_handler = AgentBusHandler(agent_client)
        return RequestHandlers(agent_bus_handler)


def safe_init(options):
    cfg = options.configuration
    RequestHandlersProxy.bus_config = BusConfig(
        username=cfg.get('bus', 'username'),
        password=cfg.get('bus', 'password'),
        host=cfg.get('bus', 'host'),
        port=int(cfg.get('bus', 'port')),
        exchange_name=cfg.get('bus', 'exchange_name'),
        exchange_type=cfg.get('bus', 'exchange_type'),
        exchange_durable=cfg.get('bus', 'exchange_durable') in ['true', 'True'],
    )


request_handlers_proxy = RequestHandlersProxy()
register(request_handlers_proxy.handle_request, CMD_RW, safe_init=safe_init, name='exec_request_handlers')
