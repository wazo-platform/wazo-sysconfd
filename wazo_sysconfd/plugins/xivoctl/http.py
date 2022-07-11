# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Body

from wazo_sysconfd.plugins.xivoctl.xivoctl import xivoctl

router = APIRouter()


@router.post('/xivoctl', status_code=200)
def get_xivoctl(body: dict = Body()):
    return xivoctl(body, None)
