# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo_sysconf.modules.agentbus_handler import AgentBusHandler, AgentBusCommand
from xivo_bus.resources.agent.event import DeleteAgentEvent, EditAgentEvent
from xivo_bus.resources.queue.event import CreateQueueEvent, EditQueueEvent,\
    DeleteQueueEvent


class TestAgentBusHandler(unittest.TestCase):

    def setUp(self):
        self.bus_publisher = Mock()
        self.handler = AgentBusHandler(self.bus_publisher)

    def test_parse_empty_command(self):
        command = ''

        expected = None
        result = self.handler._parse_command(command)

        self.assertEquals(expected, result)

    def test_parse_incomplete_command(self):
        command = 'agent.delete.'

        expected = None
        result = self.handler._parse_command(command)

        self.assertEquals(expected, result)

    def test_parse_agentbus_command(self):
        command = 'agent.delete.10'

        expected = AgentBusCommand('agent', 'delete', '10')
        result = self.handler._parse_command(command)

        self.assertEquals(expected, result)

    def test_agent_delete_command(self):
        command = 'agent.delete.1'

        self.handler.handle_command(command)

        self.bus_publisher.publish.assert_called_once_with(DeleteAgentEvent(1))

    def test_agent_edit_command(self):
        command = 'agent.edit.1'

        self.handler.handle_command(command)

        self.bus_publisher.publish.assert_called_once_with(EditAgentEvent(1))

    def test_queue_add_command(self):
        command = 'queue.add.1'

        self.handler.handle_command(command)

        self.bus_publisher.publish.assert_called_once_with(CreateQueueEvent(1))

    def test_queue_edit_command(self):
        command = 'queue.edit.1'

        self.handler.handle_command(command)

        self.bus_publisher.publish.assert_called_once_with(EditQueueEvent(1))

    def test_queue_delete_command(self):
        command = 'queue.delete.1'

        self.handler.handle_command(command)

        self.bus_publisher.publish.assert_called_once_with(DeleteQueueEvent(1))

    def test_unknown_command(self):
        command = 'foo.bar.1'

        self.handler.handle_command(command)

        self.assertFalse(self.bus_publisher.publish.called)
