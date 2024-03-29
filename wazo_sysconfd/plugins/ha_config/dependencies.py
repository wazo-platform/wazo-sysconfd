# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

from wazo_sysconfd.plugins.ha_config.ha import (
    HAConfigManager,
    _CronFileInstaller,
    _PostgresConfigUpdater,
    _SentinelFileManager,
)


@lru_cache
def get_ha_config_manager():
    return HAConfigManager(
        _PostgresConfigUpdater, _CronFileInstaller(), _SentinelFileManager()
    )
