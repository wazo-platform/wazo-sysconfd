# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Body

from wazo_sysconfd.plugins.resolv_conf.resolv_conf import resolv_conf

router = APIRouter()

@router.post('/resolv_conf', status_code=200)
def resolv_conf_post(body: dict = Body()):
    return resolv_conf(body,None)
