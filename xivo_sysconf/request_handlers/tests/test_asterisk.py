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

import unittest

from mock import ANY, Mock, patch, sentinel
from xivo_sysconf.request_handlers.asterisk import AsteriskCommandFactory, \
    AsteriskCommandExecutor


class TestAsteriskCommandFactory(unittest.TestCase):

    def setUp(self):
        self.executor = Mock()
        self.factory = AsteriskCommandFactory(self.executor)

    def test_new_command(self):
        value = 'dialplan reload'

        command = self.factory.new_command(value)

        self.assertEqual(command.value, value)
        self.assertIs(command.executor, self.executor)
        self.assertEqual(command.data, value)

    def test_new_command_with_arg(self):
        value = 'sccp reset SEP001122334455'

        command = self.factory.new_command(value)

        self.assertEqual(command.data, value)

    def test_new_command_unauthorized(self):
        value = 'foobar'

        self.assertRaises(ValueError, self.factory.new_command, value)


class TestAsteriskCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = AsteriskCommandExecutor()

    @patch('subprocess.call')
    def test_execute(self, mock_call):
        mock_call.return_value = 0

        self.executor.execute(sentinel.data)

        expected_args = ['asterisk', '-rx', sentinel.data]
        mock_call.assert_called_once_with(expected_args, stdout=ANY, close_fds=True)
