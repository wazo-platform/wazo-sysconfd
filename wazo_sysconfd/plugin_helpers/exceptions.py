# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class HttpReqError(Exception):
    def __init__(self, code: int, message: str = None):
        self.code = code
        self.message = message
