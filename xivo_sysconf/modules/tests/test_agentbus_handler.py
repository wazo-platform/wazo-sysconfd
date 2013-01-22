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


class TestAgentBusHandler(unittest.TestCase):

    def test_parse_empty_command(self):
        handler = AgentBusHandler(Mock())
        command = ''

        expected = None
        result = handler._parse_command(command)

        self.assertEquals(expected, result)

    def test_parse_incomplete_command(self):
        handler = AgentBusHandler(Mock())
        command = 'agent.delete.'

        expected = None
        result = handler._parse_command(command)

        self.assertEquals(expected, result)

    def test_parse_agentbus_command(self):
        handler = AgentBusHandler(Mock())
        command = 'agent.delete.10'

        expected = AgentBusCommand('agent', 'delete', '10')
        result = handler._parse_command(command)

        self.assertEquals(expected, result)

    def test_agent_delete_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        command = 'agent.delete.1'
        agent_id = '1'

        handler.handle_command(command)

        agent_client.on_agent_deleted.assert_called_once_with(agent_id)

    def test_agent_edit_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        command = 'agent.edit.1'
        agent_id = '1'

        handler.handle_command(command)

        agent_client.on_agent_updated.assert_called_once_with(agent_id)

    def test_queue_add_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        command = 'queue.add.1'
        queue_id = '1'

        handler.handle_command(command)

        agent_client.on_queue_added.assert_called_once_with(queue_id)

    def test_queue_edit_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        command = 'queue.edit.1'
        queue_id = '1'

        handler.handle_command(command)

        agent_client.on_queue_updated.assert_called_once_with(queue_id)

    def test_queue_delete_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        command = 'queue.delete.1'
        queue_id = '1'

        handler.handle_command(command)

        agent_client.on_queue_deleted.assert_called_once_with(queue_id)
