# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Depends, Body

from wazo_sysconfd.plugins.ha_config.ha import HAConfigManager
from wazo_sysconfd.plugins.ha_config.dependencies import get_ha_config_manager

router = APIRouter()


@router.get('/get_ha_config', status_code=200)
def get_ha_config(ha_config_manager: HAConfigManager = Depends(get_ha_config_manager)):
    return ha_config_manager.get_ha_config(None, None)


@router.post('/update_ha_config', status_code=200)
def post_update_ha_config(
    body: dict = Body(default={}),
    ha_config_manager: HAConfigManager = Depends(get_ha_config_manager),
):
    ha_config_manager.update_ha_config(body, None)
