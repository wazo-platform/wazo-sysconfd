# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import socket
import unittest

from mock import Mock, patch, sentinel
from xivo_sysconf.request_handlers.ctid import CTIdCommandExecutor


class TestCTIdCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.host = '169.254.1.1'
        self.port = 2222
        self.executor = CTIdCommandExecutor(self.host, self.port)

    @patch('socket.socket')
    def test_execute(self, mock_socket):
        sock = Mock()
        mock_socket.return_value = sock

        self.executor.execute(sentinel.data)

        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect.assert_called_once_with((self.host, self.port))
        sock.send.assert_called_once_with(sentinel.data)
        sock.close.assert_called_once_with()
