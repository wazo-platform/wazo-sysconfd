# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Body

from .services import hosts

router = APIRouter()


@router.post('/hosts', status_code=200)
def update_files(body: dict = Body()):
    hosts(body)
