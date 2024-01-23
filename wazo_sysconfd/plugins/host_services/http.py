# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Body

from .services import services

router = APIRouter()


@router.post('/services', status_code=200)
def execute_services(body: dict = Body(default={})):
    services(body)
