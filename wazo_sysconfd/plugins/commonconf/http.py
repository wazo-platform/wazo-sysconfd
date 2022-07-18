# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from fastapi import APIRouter, Body
from .services import CommonConf
from xivo.config_helper import parse_config_file


SYSCONFD_CONFIGURATION_FILE = os.path.join('/etc/wazo-sysconfd', 'config.yml')

router = APIRouter()

@router.post('/commonconf_generate', status_code=200)
def commonconf_generate():

    options = parse_config_file(SYSCONFD_CONFIGURATION_FILE)
    commonconf = CommonConf()

    commonconf.safe_init(options)
    commonconf.generate()

@router.get('/commonconf_apply', status_code=200)
def commonconf_apply():
    
    options = parse_config_file(SYSCONFD_CONFIGURATION_FILE)
    commonconf = CommonConf()

    commonconf.safe_init(options)
    commonconf.apply()
