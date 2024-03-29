# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Body

from wazo_sysconfd.plugins.resolv_conf.services import resolv_conf

router = APIRouter()


@router.post('/resolv_conf', status_code=200)
def post_resolv_conf(body: dict = Body(default={})):
    return resolv_conf(body, None)
