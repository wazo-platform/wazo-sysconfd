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

from mock import Mock, sentinel
from xivo_bus import Publisher
from xivo_bus.resources.agent.event import EditAgentEvent
from xivo_sysconf.request_handlers.agentd import AgentdCommandFactory, \
    AgentdCommandExecutor


class TestAgentdCommandFactory(unittest.TestCase):

    def setUp(self):
        self.executor = Mock()
        self.factory = AgentdCommandFactory(self.executor)

    def test_new_command(self):
        value = 'agent.edit.44'

        command = self.factory.new_command(value)

        self.assertEqual(command.value, value)
        self.assertIs(command.executor, self.executor)
        self.assertEqual(command.data, EditAgentEvent(44))

    def test_new_command_invalid_format(self):
        value = 'foobar'

        self.assertRaises(ValueError, self.factory.new_command, value)

    def test_new_command_unsupported_action(self):
        value = 'foo.bar.2'

        self.assertRaises(ValueError, self.factory.new_command, value)


class TestAgentdCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.bus_publisher = Mock(Publisher)
        self.executor = AgentdCommandExecutor(self.bus_publisher)

    def test_execute(self):
        self.executor.execute(sentinel.event)

        self.bus_publisher.publish.assert_called_once_with(sentinel.event)
