# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter
from .services import apply_commonconf, generate_commonconf

router = APIRouter()

@router.post('/commonconf_generate', status_code=200)
def commonconf_generate():

    generate_commonconf()

@router.get('/commonconf_apply', status_code=200)
def commonconf_apply():

    apply_commonconf()
