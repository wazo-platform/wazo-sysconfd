# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

from wazo_sysconfd.plugins.ha_config.ha import (
    HAConfigManager,
    _PostgresConfigUpdater,
    _CronFileInstaller,
)


class Plugin:
    def load(self, dependencies: dict):
        from .http import router
        api = dependencies['api']
        api.include_router(router)


@lru_cache()
def get_ha_config_manager():
    return HAConfigManager(_PostgresConfigUpdater, _CronFileInstaller())
