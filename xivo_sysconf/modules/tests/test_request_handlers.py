# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from mock import Mock, call, patch
from xivo_bus.resources.agent.client import AgentClient
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
        bus_config = RequestHandlersProxy.bus_config = Mock()
        proxy = RequestHandlersProxy()

        proxy.handle_request(args, options)
        proxy.handle_request(args, options)

        AgentClientMock.assert_called_once_with(fetch_response=False, config=bus_config)
        agent_client.connect.assert_called_once_with()
        AgentBusHandlerMock.assert_called_once_with(agent_client)
        RequestHandlersMock.assert_called_once_with(agent_bus_handler)
        request_handlers.read_config.assert_called_once_with()
        self.assertEqual(request_handlers.process.mock_calls,
                         [call(args, options), call(args, options)])
