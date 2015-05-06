# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import socket
import unittest

from mock import Mock, patch, sentinel
from xivo_sysconf.request_handlers.dird import DirdCommandExecutor


class TestDirdCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.host = '169.254.1.1'
        self.port = 2222

    @patch('socket.socket')
    def test_execute(self, mock_socket):
        sock = Mock()
        mock_socket.return_value = sock
        executor = DirdCommandExecutor(self.host, self.port)

        executor.execute(sentinel.data)

        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto.assert_called_once_with(sentinel.data, (self.host, self.port))
