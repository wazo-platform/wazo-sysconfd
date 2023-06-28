# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import dependencies as dependencies_module
from .request import RequestHandlersProxy
from .http import router
from .bus import EventHandler


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']
        bus_consumer = dependencies['bus_consumer']
        dependencies_module.config = dependencies['config']
        dependencies_module.bus_consumer = dependencies['bus_consumer']

        event_handler = EventHandler()
        event_handler.subscribe(bus_consumer)

        api.include_router(router)
