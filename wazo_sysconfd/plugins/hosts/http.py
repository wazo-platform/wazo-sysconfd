# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Body

from .services import hosts

router = APIRouter()


@router.put('/hosts', status_code=200)
def update_files(body: dict = Body(default={})):
    hosts(body)
