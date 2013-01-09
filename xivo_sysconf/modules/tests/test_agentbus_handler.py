# -*- coding: UTF-8 -*-

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

        commands = ['agent.delete.1']
        agent_id = '1'

        handler.handle_commands(commands)

        agent_client.on_agent_deleted.assert_called_once_with(agent_id)

    def test_agent_add_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        commands = ['agent.add.1']
        agent_id = '1'

        handler.handle_commands(commands)

        agent_client.on_agent_added.assert_called_once_with(agent_id)

    def test_queue_add_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        commands = ['queue.add.1']
        queue_id = '1'

        handler.handle_commands(commands)

        agent_client.on_queue_added.assert_called_once_with(queue_id)

    def test_queue_edit_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        commands = ['queue.edit.1']
        queue_id = '1'

        handler.handle_commands(commands)

        agent_client.on_queue_updated.assert_called_once_with(queue_id)

    def test_queue_delete_command(self):
        agent_client = Mock()
        handler = AgentBusHandler(agent_client)

        commands = ['queue.delete.1']
        queue_id = '1'

        handler.handle_commands(commands)

        agent_client.on_queue_deleted.assert_called_once_with(queue_id)
