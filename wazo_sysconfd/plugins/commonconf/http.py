# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Depends

from .dependencies import get_commonconf
from .services import CommonConf

router = APIRouter()


@router.put('/commonconf', status_code=200)
def commonconf_generate(commonconf: CommonConf = Depends(get_commonconf)):
    commonconf.generate_commonconf()


@router.get('/commonconf', status_code=200)
def commonconf_apply(commonconf: CommonConf = Depends(get_commonconf)):
    commonconf.apply_commonconf()
