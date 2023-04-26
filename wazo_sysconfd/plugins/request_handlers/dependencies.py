# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

from wazo_sysconfd.plugins.request_handlers.request import RequestHandlersProxy

config = None


@lru_cache
def get_request_handlers_proxy():
    request_handlers_proxy = RequestHandlersProxy()
    request_handlers_proxy.safe_init_from_config(config)
    request_handlers_proxy.at_start(None)
    return request_handlers_proxy
