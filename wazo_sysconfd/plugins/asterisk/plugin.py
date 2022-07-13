# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import router


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']

        api.include_router(router)
