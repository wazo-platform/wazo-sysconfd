# Copyright 2010-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.http_json_server import HttpReqError

class InternalServerErrorException(HttpReqError):
    def __init__(self, error_code, error_message):
        super().__init__(error_code, error_message)
