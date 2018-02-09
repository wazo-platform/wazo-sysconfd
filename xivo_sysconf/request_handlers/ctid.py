# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import socket

from xivo_sysconf.request_handlers.command import SimpleCommandFactory

CTIdCommandFactory = SimpleCommandFactory


class CTIdCommandExecutor(object):

    def __init__(self, host, port):
        self._addr = (host, port)

    def execute(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self._addr)
        sock.send(data)
        sock.close()
