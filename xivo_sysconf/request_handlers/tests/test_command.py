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

from mock import Mock
from xivo_sysconf.request_handlers.command import Command, SimpleCommandFactory


class TestCommand(unittest.TestCase):

    def setUp(self):
        self.value = Mock()
        self.executor = Mock()
        self.data = Mock()
        self.command = Command(self.value, self.executor, self.data)

    def test_execute(self):
        self.command.execute()

        self.executor.execute.assert_called_once_with(self.data)

    def test_execute_catch_executor_exception(self):
        self.executor.execute.side_effect = Exception()

        self.command.execute()

        self.executor.execute.assert_called_once_with(self.data)

    def test_execute_optimized(self):
        self.command.optimized = True

        self.command.execute()

        self.assertFalse(self.executor.execute.called)


class TestSimpleCommandFactory(unittest.TestCase):

    def setUp(self):
        self.executor = Mock()
        self.factory = SimpleCommandFactory(self.executor)

    def test_new_command(self):
        value = 'foobar'

        command = self.factory.new_command(value)

        self.assertEqual(command.value, value)
        self.assertIs(command.executor, self.executor)
        self.assertEqual(command.data, value)
