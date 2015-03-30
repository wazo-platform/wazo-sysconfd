# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import collections
import logging
import threading
import ConfigParser

from kombu import Connection, Exchange, Producer
from xivo.http_json_server import HttpReqError
from xivo_bus.marshaler import Marshaler
from xivo_bus.publisher import Publisher
from xivo_sysconf.request_handlers.agent import AgentCommandExecutor, \
    AgentCommandFactory
from xivo_sysconf.request_handlers.asterisk import AsteriskCommandExecutor, \
    AsteriskCommandFactory
from xivo_sysconf.request_handlers.ctid import CTICommandExecutor, \
    CTICommandFactory
from xivo_sysconf.request_handlers.dird import DirdCommandExecutor, \
    DirdCommandFactory

logger = logging.getLogger(__name__)


class Request(object):

    def __init__(self, commands):
        self.commands = commands

    def execute(self):
        for command in self.commands:
            command.execute()


class RequestFactory(object):

    def __init__(self, asterisk_command_factory, cti_command_factory, dird_command_factory, agent_command_factory):
        self._asterisk_command_factory = asterisk_command_factory
        self._cti_command_factory = cti_command_factory
        self._dird_command_factory = dird_command_factory
        self._agent_command_factory = agent_command_factory

    def new_request(self, args):
        commands = []
        # asterisk commands must be executed first
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


class DuplicateRequestOptimizer(object):

    def __init__(self, executor):
        self._executor = executor
        self._cache = set()

    def on_request_put(self, request):
        for command in request.commands:
            if command.executor != self._executor:
                continue
            if command.value in self._cache:
                command.optimized = True
            else:
                self._cache.add(command.value)

    def on_request_get(self, request):
        for command in request.commands:
            if command.executor != self._executor:
                continue
            if not command.optimized:
                self._cache.remove(command.value)


class RequestQueue(object):

    def __init__(self, optimizer):
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._queue = collections.deque()
        self._optimizer = optimizer

    def put(self, request):
        with self._lock:
            self._queue.append(request)
            self._optimizer.on_request_put(request)
            self._condition.notify()

    def get(self):
        with self._lock:
            while not self._queue:
                self._condition.wait()
            request = self._queue.popleft()
            self._optimizer.on_request_get(request)
        return request


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
        request_optimizer = DuplicateRequestOptimizer(asterisk_command_executor)
        request_queue = RequestQueue(request_optimizer)
        request_handlers = RequestHandlers(request_factory, request_queue)
        request_processor = RequestProcessor(request_queue)

        # start the request processor thread
        t = threading.Thread(target=request_processor.run)
        t.daemon = True
        t.start()

        self._request_handlers = request_handlers

    def handle_request(self, args, options):
        return self._request_handlers.handle_request(args, options)
