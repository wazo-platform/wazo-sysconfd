# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock, sentinel
from xivo_bus import Publisher
from xivo_bus.resources.agent.event import EditAgentEvent
from wazo_sysconfd.request_handlers.agentd import (
    AgentdCommandFactory,
    AgentdCommandExecutor,
)


class TestAgentdCommandFactory(unittest.TestCase):

    def setUp(self):
        self.executor = Mock()
        self.factory = AgentdCommandFactory(self.executor)

    def test_new_command(self):
        value = 'agent.edit.44'
        request = Mock()

        command = self.factory.new_command(value, request)

        self.assertEqual(command.value, value)
        self.assertIs(command.executor, self.executor)
        self.assertEqual(command.data, EditAgentEvent(44))
        self.assertEqual(command.requests, {request})

    def test_new_command_invalid_format(self):
        value = 'foobar'
        request = Mock()

        self.assertRaises(ValueError, self.factory.new_command, value, request)

    def test_new_command_unsupported_action(self):
        value = 'foo.bar.2'
        request = Mock()

        self.assertRaises(ValueError, self.factory.new_command, value, request)


class TestAgentdCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.bus_publisher = Mock(Publisher)
        self.executor = AgentdCommandExecutor(self.bus_publisher)

    def test_execute(self):
        command = Mock()

        self.executor.execute(command, sentinel.event)

        self.bus_publisher.publish.assert_called_once_with(sentinel.event)
