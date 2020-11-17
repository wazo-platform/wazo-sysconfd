# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import logging
import threading

from kombu import Connection, Exchange, Producer
from xivo.http_json_server import HttpReqError
from xivo_bus.marshaler import Marshaler
from xivo_bus.publisher import FailFastPublisher

from .agentd import (
    AgentdCommandExecutor,
    AgentdCommandFactory,
)
from .asterisk import (
    AsteriskCommandExecutor,
    AsteriskCommandFactory,
)
from .chown_autoprov_config import (
    ChownAutoprovCommandExecutor,
    ChownAutoprovCommandFactory,
)

logger = logging.getLogger(__name__)


class Request(object):

    def __init__(self, commands):
        self.commands = commands
        self.observer = None

    def execute(self):
        for command in self.commands:
            command.execute()
        if self.observer is not None:
            self.observer.on_request_executed()


class RequestFactory(object):

    def __init__(self,
                 agentd_command_factory,
                 asterisk_command_factory,
                 chown_autoprov_command_factory):
        self._agentd_command_factory = agentd_command_factory
        self._asterisk_command_factory = asterisk_command_factory
        self._chown_autoprov_command_factory = chown_autoprov_command_factory

    def new_request(self, args):
        commands = []
        # asterisk commands must be executed first
        self._append_commands('ipbx', self._asterisk_command_factory, args, commands)
        self._append_commands('agentbus', self._agentd_command_factory, args, commands)
        self._append_commands('chown_autoprov_config', self._chown_autoprov_command_factory, args, commands)
        return Request(commands)

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
            self._queue_request(request)

    def _queue_request(self, request):
        self._request_queue.put(request)


class SyncRequestObserver(object):

    def __init__(self, timeout=30):
        self._event = threading.Event()
        self._timeout = timeout

    def on_request_executed(self):
        self._event.set()

    def wait(self):
        return self._event.wait(self._timeout)


class SyncRequestHandlers(RequestHandlers):

    def _queue_request(self, request):
        request.observer = SyncRequestObserver()
        super(SyncRequestHandlers, self)._queue_request(request)
        if not request.observer.wait():
            logger.warning('timeout reached on synchronous request')


class LazyBusPublisher(object):

    def __init__(self, bus_connection, bus_exchange, marshaler):
        self._bus_connection = bus_connection
        self._bus_exchange = bus_exchange
        self._marshaler = marshaler
        self._publisher = None

    def publish(self, event):
        if self._publisher is None:
            self._publisher = self._new_publisher()
        return self._publisher.publish(event)

    def _new_publisher(self):
        bus_producer = Producer(self._bus_connection, self._bus_exchange, auto_declare=True)
        return FailFastPublisher(bus_producer, self._marshaler)


class RequestHandlersProxy(object):

    def __init__(self):
        self._request_handlers = None
        self._request_processor = None

    def safe_init(self, options):
        # read config from main configuration file
        config = options.configuration
        synchronous = config.getboolean('request_handlers', 'synchronous')
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
        bus_publisher = LazyBusPublisher(bus_connection, bus_exchange, Marshaler(uuid))

        # instantiate executors
        agentd_command_executor = AgentdCommandExecutor(bus_publisher)
        asterisk_command_executor = AsteriskCommandExecutor(bus_publisher)
        chown_autoprov_command_executor = ChownAutoprovCommandExecutor()

        # instantiate factories
        agentd_command_factory = AgentdCommandFactory(agentd_command_executor)
        asterisk_command_factory = AsteriskCommandFactory(asterisk_command_executor)
        chown_autoprov_command_factory = ChownAutoprovCommandFactory(chown_autoprov_command_executor)

        # instantiate other stuff
        request_factory = RequestFactory(agentd_command_factory,
                                         asterisk_command_factory,
                                         chown_autoprov_command_factory)
        request_optimizer = DuplicateRequestOptimizer(asterisk_command_executor)
        request_queue = RequestQueue(request_optimizer)
        if synchronous:
            self._request_handlers = SyncRequestHandlers(request_factory, request_queue)
        else:
            self._request_handlers = RequestHandlers(request_factory, request_queue)
        self._request_processor = RequestProcessor(request_queue)

    def at_start(self, options):
        t = threading.Thread(target=self._request_processor.run)
        t.daemon = True
        t.start()

    def handle_request(self, args, options):
        return self._request_handlers.handle_request(args, options)
