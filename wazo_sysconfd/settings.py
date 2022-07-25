# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

from wazo_sysconfd.main import config
from wazo_sysconfd.plugins.asterisk.asterisk import Asterisk
from wazo_sysconfd.request_handlers.request import RequestHandlersProxy


@lru_cache()
def get_asterisk():
    return Asterisk()


@lru_cache()
def get_request_handlers_proxy():
    request_handlers_proxy = RequestHandlersProxy()
    request_handlers_proxy.safe_init_from_config(config)
    request_handlers_proxy.at_start(None)
    return request_handlers_proxy
