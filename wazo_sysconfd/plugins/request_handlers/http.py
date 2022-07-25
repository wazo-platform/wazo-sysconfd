# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Depends, Body
from wazo_sysconfd.request_handlers.request import RequestHandlersProxy
from wazo_sysconfd.settings import get_request_handlers_proxy

router = APIRouter()


@router.post('/exec_request_handlers', status_code=200)
def exec_request_handlers(
    body: dict = Body(),
    request_handlers_proxy: RequestHandlersProxy = Depends(get_request_handlers_proxy),
):
    return request_handlers_proxy.handle_request(body, None)
