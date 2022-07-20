# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from .http import router
from .services import safe_init
from xivo.config_helper import parse_config_file


SYSCONFD_CONFIGURATION_FILE = os.path.join('/etc/wazo-sysconfd', 'config.yml')
class Plugin:
    def load(self, dependencies: dict):
        options = parse_config_file(SYSCONFD_CONFIGURATION_FILE)

        safe_init(options)
        api = dependencies['api']
        api.include_router(router)
