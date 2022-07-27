# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import router
from . import dependencies as dependencies_module


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']
        dependencies_module.status_aggregator = dependencies['status_aggregator']

        api.include_router(router)
