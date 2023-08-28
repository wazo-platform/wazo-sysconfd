# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_sysconfd.bus import BusConsumerProxy

from . import dependencies as dependencies_module
from .events_handler import EventHandler
from .http import router


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']
        config = dependencies['config']
        bus_proxy: BusConsumerProxy = dependencies['get_bus_consumer']()

        dependencies_module.config = dependencies['config']

        events_handler = EventHandler(config['uuid'], bus_proxy)
        events_handler.subscribe()

        api.include_router(router)
