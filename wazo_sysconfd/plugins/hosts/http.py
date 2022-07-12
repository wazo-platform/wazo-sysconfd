# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from fastapi import APIRouter, Body
from wazo_sysconfd.modules.resolvconf import safe_init, Hosts
from xivo.config_helper import parse_config_file


SYSCONFD_CONFIGURATION_FILE = os.path.join('/etc/wazo-sysconfd', 'config.yml')

router = APIRouter()

@router.post('/hosts', status_code=200)
def update_files(body: dict = Body()):
    
    options = parse_config_file(SYSCONFD_CONFIGURATION_FILE)

    safe_init(options)
    Hosts(body)
