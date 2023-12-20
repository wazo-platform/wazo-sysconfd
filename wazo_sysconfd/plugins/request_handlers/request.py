# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import logging
import threading
import uuid

from xivo_bus.publisher import BusPublisher
from xivo_bus.resources.sysconfd.event import RequestHandlersProgressEvent

from wazo_sysconfd.plugin_helpers.exceptions import HttpReqError
from wazo_sysconfd.plugins.request_handlers.asterisk import (
    AsteriskCommandExecutor,
    AsteriskCommandFactory,
)
from wazo_sysconfd.plugins.request_handlers.chown_autoprov_config import (
    ChownAutoprovCommandExecutor,
    ChownAutoprovCommandFactory,
)

logger = logging.getLogger(__name__)


class Request:
    def __init__(self, commands, context=None):
        self.commands = commands
        self.observers = []
        self.uuid = str(uuid.uuid4())
        self.context = context

    def execute(self):
        for command in self.commands:
            command.execute()
        for observer in self.observers:
            observer.on_request_executed(self)


class RequestFactory:
    def __init__(self, asterisk_command_factory, chown_autoprov_command_factory):
        self._factories = {
            'ipbx': asterisk_command_factory,
            'chown_autoprov_config': chown_autoprov_command_factory,
        }

    def new_request(self, args, **options):
        request = Request([], context=args.get('context'))
        # asterisk commands must be executed first
        self._generate_asterisk_commands(request, args, **options)
        self._generate_autoprov_commands(request, args, **options)
        return request

    def _generate_asterisk_commands(self, request: Request, args, **options):
        self._generate_commands('ipbx', request, args, **options)

    def _generate_autoprov_commands(self, request: Request, args, **options):
        self._generate_commands('chown_autoprov_config', request, args, **options)

    def _generate_commands(self, category: str, request: Request, args, **options):
        try:
            factory = self._factories[category]
        except KeyError:
            return

        for value in args.get(category, []):
            try:
                command = factory.new_command(value, request, **options)
            except ValueError as e:
                logger.warning('Invalid "%s" command %r: %s', category, value, e)
            except Exception:
                logger.exception(
                    'Error while creating "%s" command %r', category, value
                )
            else:
                request.commands.append(command)


class DuplicateRequestOptimizer:
    def __init__(self, executor):
        self._executor = executor
        self._cache = {}
        self._lock = threading.RLock()

    def on_request_put(self, request):
        for command in request.commands:
            if command.executor != self._executor:
                continue
            with self._lock:
                if command.value in self._cache:
                    command.optimized = True
                    actual_command = self._cache[command.value]
                    actual_command.requests.add(request)
                else:
                    self._cache[command.value] = command

    def on_request_get(self, request):
        for command in request.commands:
            if command.executor != self._executor:
                continue
            with self._lock:
                if not command.optimized:
                    self._cache.pop(command.value, None)


class RequestQueue:
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


class RequestProcessor:
    def __init__(self, request_queue):
        self._request_queue = request_queue

    def run(self):
        while True:
            try:
                request = self._request_queue.get()
                request.execute()
            except Exception:
                logger.exception('Unexpected error')


class RequestHandlers:
    def __init__(self, request_factory, request_queue, bus_publisher):
        self._request_factory = request_factory
        self._request_queue = request_queue
        self._bus_publisher = bus_publisher

    def handle_request(self, args, options):
        options = options or {}
        try:
            request = self._request_factory.new_request(args, **options)
        except Exception:
            logger.exception('Error while creating new request %s', args)
            raise HttpReqError(400)
        else:
            self._add_completed_observer(request)
            self._queue_request(request)
        return request.uuid

    def _queue_request(self, request):
        self._request_queue.put(request)

    def _add_completed_observer(self, request):
        observer = RequestCompletedEventObserver(self._bus_publisher)
        request.observers.append(observer)


class RequestCompletedEventObserver:
    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher

    def on_request_executed(self, request):
        self._bus_publisher.publish(
            RequestHandlersProgressEvent(
                request.uuid, request.context, status='completed'
            )
        )


class SyncRequestObserver:
    def __init__(self, timeout=30):
        self._event = threading.Event()
        self._timeout = timeout

    def on_request_executed(self, request):
        self._event.set()

    def wait(self):
        return self._event.wait(self._timeout)


class SyncRequestHandlers(RequestHandlers):
    def _queue_request(self, request):
        observer = SyncRequestObserver()
        request.observers.append(observer)
        super()._queue_request(request)
        if not observer.wait():
            logger.warning('timeout reached on synchronous request')


class RequestHandlersProxy:
    def __init__(self):
        self._request_handlers = None
        self._request_processor = None

    def safe_init(self, options):
        # read config from main configuration file
        config = options.configuration
        self.safe_init_from_config(config)

    def safe_init_from_config(self, config):
        synchronous = config.get('request_handlers', {}).get('synchronous')
        uuid = config.get('uuid', None)
        bus_config = config.get('bus', {})

        # instantiate bus publisher
        bus_publisher = BusPublisher(
            name='wazo-sysconfd', service_uuid=uuid, **bus_config
        )

        # instantiate executors
        asterisk_command_executor = AsteriskCommandExecutor(bus_publisher)
        chown_autoprov_command_executor = ChownAutoprovCommandExecutor()

        # instantiate factories
        asterisk_command_factory = AsteriskCommandFactory(asterisk_command_executor)
        chown_autoprov_command_factory = ChownAutoprovCommandFactory(
            chown_autoprov_command_executor
        )

        # instantiate other stuff
        request_factory = RequestFactory(
            asterisk_command_factory, chown_autoprov_command_factory
        )
        request_optimizer = DuplicateRequestOptimizer(asterisk_command_executor)
        request_queue = RequestQueue(request_optimizer)
        if synchronous:
            self._request_handlers = SyncRequestHandlers(
                request_factory, request_queue, bus_publisher
            )
        else:
            self._request_handlers = RequestHandlers(
                request_factory, request_queue, bus_publisher
            )
        self._request_processor = RequestProcessor(request_queue)

    def at_start(self, options):
        t = threading.Thread(target=self._request_processor.run)
        t.daemon = True
        t.start()

    def handle_request(self, args, options):
        request_uuid = self._request_handlers.handle_request(args, options)
        return {
            'request_uuid': request_uuid,
        }
