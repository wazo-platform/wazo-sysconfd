# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import router
from .resolv_conf import safe_init


class Plugin:
    def load(self, dependencies: dict):
        safe_init(dependencies['config'])
        api = dependencies['api']
        api.include_router(router)
