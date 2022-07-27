# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_sysconfd.modules import resolvconf
from .http import router


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']
        config = dependencies['config']
        resolvconf.safe_init(config)
        api.include_router(router)
