# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_sysconfd.bus import BusConsumerProxy

from . import dependencies as dependencies_module
from .http import router


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']
        bus_proxy: BusConsumerProxy = dependencies['get_bus_consumer']()
        dependencies_module.status_aggregator = dependencies['status_aggregator']
        dependencies_module.status_aggregator.add_provider(bus_proxy.provide_status)

        api.include_router(router)
