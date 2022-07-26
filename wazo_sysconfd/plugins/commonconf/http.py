# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Depends
from .services import CommonConf
from .plugin import get_commonconf

router = APIRouter()

@router.post('/commonconf_generate', status_code=200)
def commonconf_generate(commonconf: CommonConf = Depends(get_commonconf)):

    commonconf.generate_commonconf()

@router.get('/commonconf_apply', status_code=200)
def commonconf_apply(commonconf: CommonConf = Depends(get_commonconf)):

    commonconf.apply_commonconf()
