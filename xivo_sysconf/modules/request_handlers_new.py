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

import logging
import os
import re
import socket
import subprocess
import threading
import ConfigParser
from Queue import Queue

from kombu import Connection, Exchange, Producer
from xivo.http_json_server import register, CMD_RW, HttpReqError
from xivo_bus.marshaler import Marshaler
from xivo_bus.publisher import Publisher
from xivo_bus.resources.agent.event import DeleteAgentEvent, EditAgentEvent
from xivo_bus.resources.queue.event import CreateQueueEvent, DeleteQueueEvent, EditQueueEvent

logger = logging.getLogger(__name__)


class Command(object):

    def __init__(self, value, executor, data):
        self._value = value
        self._executor = executor
        self._data = data

    def execute(self):
        logger.info('Executing %s command %s...', self._executor.name, self._value)
        try:
            self._executor.execute(self._data)
        except Exception:
            logger.exception('Error while executing %s command %s', self._executor.name, self._value)


class SimpleCommandFactory(object):

    def __init__(self, executor):
        self._executor = executor

    def new_command(self, value):
        return Command(value, self._executor, value)


class AgentCommandFactory(object):

    _REGEX = re.compile(r'^(\w+\.\w+)\.(\d+)$')
    _ACTION_MAP = {
        'agent.edit': EditAgentEvent,
        'agent.delete': DeleteAgentEvent,
        'queue.add': CreateQueueEvent,
        'queue.edit': EditQueueEvent,
        'queue.delete': DeleteQueueEvent,
    }

    def __init__(self, agent_command_executor):
        self._executor = agent_command_executor

    def new_command(self, value):
        action, id_ = self._extract_action_and_id(value)
        event = self._new_event(action, id_)
        return Command(value, self._executor, event)

    def _extract_action_and_id(self, value):
        match = self._REGEX.match(value)
        if not match:
            raise ValueError('could not extract action and ID')

        return match.groups()

    def _new_event(self, action, id_):
        event_class = self._ACTION_MAP.get(action)
        if event_class is None:
            raise ValueError('unsupported action')

        return event_class(id_)


class AgentCommandExecutor(object):

    name = 'agentbus'

    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher

    def execute(self, event):
        self._bus_publisher.publish(event)


CTICommandFactory = SimpleCommandFactory


class CTICommandExecutor(object):

    name = 'ctibus'

    def __init__(self, host, port):
        self._addr = (host, port)

    def execute(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self._addr)
        sock.send(data)
        sock.close()


DirdCommandFactory = SimpleCommandFactory


class DirdCommandExecutor(object):

    name = 'dird'

    def __init__(self, host, port):
        self._addr = (host, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def execute(self, data):
        self._sock.sendto(data, self._addr)


class AsteriskCommandFactory(object):

    _COMMANDS = [
        'core reload',
        'core restart now',
        'dialplan reload',
        'sip reload',
        'moh reload',
        'iax2 reload',
        'module reload app_queue.so',
        'module reload app_meetme.so',
        'features reload',
        'voicemail reload',
        'module reload chan_sccp.so',
    ]
    _ARG_COMMANDS = [
        'sccp reset'
    ]

    def __init__(self, asterisk_command_executor):
        self._executor = asterisk_command_executor

    def new_command(self, value):
        self._check_validity(value)
        return Command(value, self._executor, value)

    def _check_validity(self, value):
        if value in self._COMMANDS:
            return
        for arg_cmd in self._ARG_COMMANDS:
            if value.startswith(arg_cmd):
                return
        raise ValueError('unauthorized command')


class AsteriskCommandExecutor(object):

    name = 'ipbx'

    def __init__(self):
        self._null = open(os.devnull)

    def execute(self, data):
        exit_code = subprocess.call(['asterisk', '-rx', data], stdout=self._null, close_fds=True)
        if exit_code:
            logger.error('asterisk returned non-zero status code %s', exit_code)


class Request(object):

    def __init__(self, commands):
        self._commands = commands

    def execute(self):
        for command in self._commands:
            command.execute()


class RequestFactory(object):

    def __init__(self, asterisk_command_factory, cti_command_factory, dird_command_factory, agent_command_factory):
        self._asterisk_command_factory = asterisk_command_factory
        self._cti_command_factory = cti_command_factory
        self._dird_command_factory = dird_command_factory
        self._agent_command_factory = agent_command_factory

    def new_request(self, args):
        commands = []
        # asterisk commands must be the executed first
        self._append_asterisk_commands(args, commands)
        self._append_cti_commands(args, commands)
        self._append_dird_commands(args, commands)
        self._append_agent_commands(args, commands)
        return Request(commands)

    def _append_asterisk_commands(self, args, commands):
        self._append_commands('ipbx', self._asterisk_command_factory, args, commands)

    def _append_cti_commands(self, args, commands):
        self._append_commands('ctibus', self._cti_command_factory, args, commands)

    def _append_dird_commands(self, args, commands):
        self._append_commands('dird', self._dird_command_factory, args, commands)

    def _append_agent_commands(self, args, commands):
        self._append_commands('agentbus', self._agent_command_factory, args, commands)

    def _append_commands(self, key, factory, args, commands):
        values = args.get(key)
        if not values:
            return

        for value in values:
            try:
                command = factory.new_command(value)
            except ValueError as e:
                logger.warning('Invalid "%s" command %r: %s', key, value, e)
            except Exception:
                logger.exception('Error while creating "%s" command %r', key, value)
            else:
                commands.append(command)


class RequestProcessor(object):

    def __init__(self, request_queue):
        self._request_queue = request_queue

    def run(self):
        while True:
            try:
                request = self._request_queue.get()
                request.execute()
            except Exception:
                logger.exception('Unexpected error')


class RequestHandlers(object):

    def __init__(self, request_factory, request_queue):
        self._request_factory = request_factory
        self._request_queue = request_queue

    def handle_request(self, args, options):
        try:
            request = self._request_factory.new_request(args)
        except Exception:
            logger.exception('Error while creating new request %s', args)
            raise HttpReqError(400)
        else:
            self._request_queue.put(request)


class RequestHandlersProxy(object):

    _SOCKET_CONFFILE = '/etc/xivo/sysconfd/socket.conf'

    def __init__(self):
        self._request_handlers = None

    def configure(self, options):
        # read config from socket.conf
        conf_obj = ConfigParser.RawConfigParser()
        with open(self._SOCKET_CONFFILE) as fobj:
            conf_obj.readfp(fobj)
        ctibus_host = conf_obj.get('ctibus', 'bindaddr')
        ctibus_port = conf_obj.getint('ctibus', 'port')
        dirdbus_host = conf_obj.get('dirdbus', 'bindaddr')
        dirdbus_port = conf_obj.getint('dirdbus', 'port')

        # read config from main configuration file
        config = options.configuration
        username = config.get('bus', 'username')
        password = config.get('bus', 'password')
        host = config.get('bus', 'host')
        port = config.getint('bus', 'port')
        exchange_name = config.get('bus', 'exchange_name')
        exchange_type = config.get('bus', 'exchange_type')
        exchange_durable = config.getboolean('bus', 'exchange_durable')

        # instantiate bus publisher
        # XXX should fetch the uuid from the config
        uuid = None
        url = 'amqp://{username}:{password}@{host}:{port}//'.format(username=username,
                                                                    password=password,
                                                                    host=host,
                                                                    port=port)
        bus_connection = Connection(url)
        bus_exchange = Exchange(exchange_name, exchange_type, durable=exchange_durable)
        bus_producer = Producer(bus_connection, bus_exchange, auto_declare=True)
        bus_publisher = Publisher(bus_producer, Marshaler(uuid))

        # instantiate executors
        agent_command_executor = AgentCommandExecutor(bus_publisher)
        asterisk_command_executor = AsteriskCommandExecutor()
        cti_command_executor = CTICommandExecutor(ctibus_host, ctibus_port)
        dird_command_executor = DirdCommandExecutor(dirdbus_host, dirdbus_port)

        # instantiate factories
        agent_command_factory = AgentCommandFactory(agent_command_executor)
        asterisk_command_factory = AsteriskCommandFactory(asterisk_command_executor)
        cti_command_factory = CTICommandFactory(cti_command_executor)
        dird_command_factory = DirdCommandFactory(dird_command_executor)

        # instantiate other stuff
        request_factory = RequestFactory(asterisk_command_factory, cti_command_factory, dird_command_factory, agent_command_factory)
        request_queue = Queue()
        request_handlers = RequestHandlers(request_factory, request_queue)
        request_processor = RequestProcessor(request_queue)

        # start the request processor thread
        t = threading.Thread(target=request_processor.run)
        t.daemon = True
        t.start()

        self._request_handlers = request_handlers

    def handle_request(self, args, options):
        return self._request_handlers.handle_request(args, options)


proxy = RequestHandlersProxy()
register(proxy.handle_request, CMD_RW, safe_init=proxy.configure,
         name='exec_request_handlers2')
