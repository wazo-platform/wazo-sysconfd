# -*- coding: UTF-8 -*-

import unittest

from mock import Mock, call, patch
from xivo_agent.ctl.client import AgentClient
from xivo_sysconf.modules.agentbus_handler import AgentBusHandler
from xivo_sysconf.modules.request_handlers import RequestHandlers, \
    RequestHandlersProxy


class TestRequestHandlers(unittest.TestCase):

    def test_process_agentbus_commands(self):
        agent_bus_handler = Mock()
        handler = RequestHandlers(agent_bus_handler)

        agent_command = 'agent.add.1'

        commands = {
            'ipbx': [],
            'ctibus': [],
            'dird': [],
            'agentbus': [agent_command],
        }

        handler.process(commands, Mock())

        agent_bus_handler.handle_command.assert_called_once_with(agent_command)


class TestRequestHandlersProxy(unittest.TestCase):

    @patch('xivo_sysconf.modules.request_handlers.AgentClient')
    @patch('xivo_sysconf.modules.request_handlers.AgentBusHandler')
    @patch('xivo_sysconf.modules.request_handlers.RequestHandlers')
    def test_handle_request(self, RequestHandlersMock, AgentBusHandlerMock, AgentClientMock):
        agent_client = Mock(AgentClient)
        AgentClientMock.return_value = agent_client
        agent_bus_handler = Mock(AgentBusHandler)
        AgentBusHandlerMock.return_value = agent_bus_handler
        request_handlers = Mock(RequestHandlers)
        RequestHandlersMock.return_value = request_handlers
        args = Mock()
        options = Mock()
        proxy = RequestHandlersProxy()

        proxy.handle_request(args, options)
        proxy.handle_request(args, options)

        AgentClientMock.assert_called_once_with()
        agent_client.connect.assert_called_once_with()
        AgentBusHandlerMock.assert_called_once_with(agent_client)
        RequestHandlersMock.assert_called_once_with(agent_bus_handler)
        request_handlers.read_config.assert_called_once_with()
        self.assertEqual(request_handlers.process.mock_calls,
                         [call(args, options), call(args, options)])
