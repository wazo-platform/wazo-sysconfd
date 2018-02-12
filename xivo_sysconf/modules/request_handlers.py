# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo.http_json_server import register, CMD_RW
from xivo_sysconf.request_handlers.request import RequestHandlersProxy


proxy = RequestHandlersProxy()
register(proxy.handle_request, CMD_RW, safe_init=proxy.safe_init, at_start=proxy.at_start,
         name='exec_request_handlers')
