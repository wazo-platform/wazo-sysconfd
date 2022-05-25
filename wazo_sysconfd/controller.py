# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from typing import List
from xivo import plugin_helpers
from xivo.status import StatusAggregator

from .http_server import api, SysconfdApplication

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config: dict):
        self.config = config
        self.http_server = SysconfdApplication('%(prog)s', config=config)
        self.status_aggregator = StatusAggregator()

        plugin_helpers.load(
            namespace='wazo_sysconfd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
                'status_aggregator': self.status_aggregator,
            }
        )
        logger.debug('Loaded routes:\n%s', self.list_routes())

    def list_routes(self) -> List:
        url_list = [
            {'path': route.path, 'name': route.name}
            for route in api.routes
        ]
        return url_list

    def run(self):
        logger.info('wazo-sysconfd starting...')
        self.http_server.run()
