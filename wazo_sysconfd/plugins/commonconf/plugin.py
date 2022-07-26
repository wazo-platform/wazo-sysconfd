# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

from .services import CommonConf


config = None


class Plugin:
    def load(self, dependencies: dict):
        from .http import router
        global config

        api = dependencies['api']
        config = dependencies['config']

        api.include_router(router)


@lru_cache()
def get_commonconf():
    commonconf = CommonConf()
    commonconf.safe_init(config)
    return commonconf
