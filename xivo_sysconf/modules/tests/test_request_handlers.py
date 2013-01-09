# -*- coding: UTF-8 -*-

import unittest

from mock import Mock
from xivo_sysconf.modules.request_handlers import RequestHandlers


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
