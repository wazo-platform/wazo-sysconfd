# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import router
from .services import safe_init

class Plugin:
    def load(self, dependencies: dict):
        options = dependencies['config']

        safe_init(options)
        api = dependencies['api']
        api.include_router(router)
