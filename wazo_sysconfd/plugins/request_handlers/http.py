# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from fastapi import APIRouter, Depends, Body

from wazo_sysconfd.plugins.request_handlers.dependencies import (
    get_request_handlers_proxy,
)
from wazo_sysconfd.plugins.request_handlers.request import RequestHandlersProxy

router = APIRouter()


@router.post('/exec_request_handlers', status_code=200)
def exec_request_handlers(
    body: dict = Body(default={}),
    request_handlers_proxy: RequestHandlersProxy = Depends(get_request_handlers_proxy),
):
    body['from_wazo_uuid'] = os.getenv('XIVO_UUID', None)
    return request_handlers_proxy.handle_request(body, None)
