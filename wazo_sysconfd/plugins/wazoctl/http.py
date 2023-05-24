# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Body

from wazo_sysconfd.plugins.wazoctl.wazoctl import wazoctl

router = APIRouter()


@router.put('/wazoctl', status_code=200)
def get_wazoctl(body: dict = Body(default={})):
    return wazoctl(body, None)
