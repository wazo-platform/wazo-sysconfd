# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from typing import Callable

from functools import lru_cache
from gunicorn.util import _setproctitle
from multiprocessing.managers import BaseManager, BaseProxy

from xivo.status import Status, StatusDict
from xivo_bus.consumer import BusConsumer as Consumer
from xivo_bus.publisher import BusPublisher as Publisher

from .plugins.request_handlers import dependencies as request_handlers_deps


class BusConsumer(Consumer):
    def __init__(self, wazo_uuid, **bus_config):
        super().__init__('wazo-sysconfd', **bus_config)
        self._wazo_uuid: str = wazo_uuid

    @classmethod
    def from_config(cls, config: dict):
        return cls(config['uuid'], **config['bus'])

    # Override ConsumerMixin to add headers to callbacks
    def _ConsumerMixin__dispatch(
        self, event_name: str, payload: dict, headers: dict = None
    ):
        with self._ConsumerMixin__lock:
            subscriptions = self._ConsumerMixin__subscriptions[event_name].copy()
        for handler, _ in subscriptions:
            try:
                handler(payload, headers)
            except Exception:
                self.log.exception(
                    'Handler \'%s\' for event \'%s\' failed',
                    getattr(handler, '__name__', handler),
                    event_name,
                )


class BusConsumerProxy(BaseProxy):
    _exposed_ = (
        '__getattribute__',
        'consumer_connected',
        'provide_status',
        'subscribe',
        'unsubscribe',
    )

    def consumer_connected(self) -> bool:
        return self._callmethod('consumer_connected', ())

    def provide_status(self, status: StatusDict) -> None:
        status['bus_consumer']['status'] = (
            Status.ok if self._callmethod('consumer_connected', ()) else Status.fail
        )

    def subscribe(
        self,
        event_name: str,
        handler: Callable[[dict, dict], None],
        headers: dict | None = None,
        routing_key: str | None = None,
        headers_match_all: bool = True,
    ) -> None:
        return self._callmethod(
            'subscribe', (event_name, handler, headers, routing_key, headers_match_all)
        )

    def unsubscribe(
        self, event_name: str, handler: Callable[[dict, dict], None]
    ) -> None:
        return self._callmethod('unsubscribe', (event_name, handler))

    @property
    def is_running(self) -> bool:
        return self._callmethod('__getattribute__', ('is_running',))


class BusManager:
    class _ProxyManager(BaseManager):
        pass

    def __init__(self, config: dict):
        self._config: dict = config
        self._manager = self._ProxyManager()
        self._manager.register('bus_consumer', self._consumer, BusConsumerProxy)

    @lru_cache
    def _consumer(self) -> BusConsumer:
        return BusConsumer.from_config(self._config)

    def _initialize(self, config: dict) -> None:
        _setproctitle('bus manager [sysconfd]')

        # Note: must call so request_handler callback can work in bus process, since
        # it will be configured after the bus process has already started
        request_handlers_deps.config = config

        bus_consumer = self._consumer()
        bus_consumer.start()

    def get_consumer(self) -> BusConsumerProxy:
        return self._manager.bus_consumer()

    def start(self) -> None:
        self._manager.start(self._initialize, (self._config,))

    def stop(self) -> None:
        self._manager.shutdown()
        self._manager.join()


class BusPublisher(Publisher):
    @classmethod
    def from_config(cls, service_uuid: str, bus_config: dict):
        return cls(name='wazo-sysconfd', service_uuid=service_uuid, **bus_config)
