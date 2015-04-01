# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo.http_json_server import register, CMD_RW
from xivo_sysconf.request_handlers.request import RequestHandlersProxy


proxy = RequestHandlersProxy()
register(proxy.handle_request, CMD_RW, safe_init=proxy.safe_init, at_start=proxy.at_start,
         name='exec_request_handlers')
