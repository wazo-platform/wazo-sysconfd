# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.http_json_server import register, CMD_RW
from wazo_sysconfd.request_handlers.request import RequestHandlersProxy


proxy = RequestHandlersProxy()
register(proxy.handle_request, CMD_RW, safe_init=proxy.safe_init, at_start=proxy.at_start,
         name='exec_request_handlers')
