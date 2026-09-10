# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from . import dependencies as dependencies_module
from .http import router

logger = logging.getLogger(__name__)

logger.info("Loading config_diff plugin")


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']
        config = dependencies['config']
        logger.debug('AFDEBUG: config: %s', config)
        dependencies_module.config = config['config_diff']

        api.include_router(router)
