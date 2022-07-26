# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

from .asterisk import Asterisk


class Plugin:
    def load(self, dependencies: dict):
        from .http import router
        api = dependencies['api']

        api.include_router(router)


@lru_cache()
def get_asterisk():
    return Asterisk()
