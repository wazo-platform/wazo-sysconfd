# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo.status import StatusAggregator

from .http_server import SysconfdApplication

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config: dict):
        self.config = config
        self.http_server = SysconfdApplication('%(prog)s', config=config)
        self.status_aggregator = StatusAggregator()

    def run(self):
        logger.info('wazo-sysconfd starting...')
        self.http_server.run()
