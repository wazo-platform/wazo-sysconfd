# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import logging

from xivo import plugin_helpers
from xivo.status import StatusAggregator
from .bus import BusConsumer

from .http_server import api, SysconfdApplication

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config: dict):
        self.config = config
        self.http_server = SysconfdApplication('%(prog)s', config=config)
        self.status_aggregator = StatusAggregator()
        self.bus_consumer = BusConsumer.from_config(config['bus'])
        self.status_aggregator.add_provider(self.bus_consumer.provide_status)

        plugin_manager = plugin_helpers.load(
            namespace='wazo_sysconfd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'bus_consumer': self.bus_consumer,
                'config': config,
                'status_aggregator': self.status_aggregator,
            },
        )
        logger.debug('Loaded plugins:\n%s', plugin_manager.names())
        logger.debug('Loaded routes:\n%s', self.list_routes())

    def list_routes(self) -> list:
        url_list = [{'path': route.path, 'name': route.name} for route in api.routes]
        return url_list

    def run(self):
        logger.info('wazo-sysconfd starting...')
        with self.bus_consumer:
            self.http_server.run()
