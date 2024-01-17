# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock, patch, sentinel

from wazo_bus import BusPublisher
from wazo_sysconfd.plugins.request_handlers.asterisk import (
    AsteriskCommandFactory,
    AsteriskCommandExecutor,
)


class TestAsteriskCommandFactory(unittest.TestCase):
    def setUp(self):
        self.executor = Mock()
        self.factory = AsteriskCommandFactory(self.executor)
        self.wazo_uuid = str(uuid4())

    def test_new_command(self):
        value = 'dialplan reload'
        request = Mock()

        command = self.factory.new_command(value, request)

        self.assertEqual(command.value, value)
        self.assertIs(command.executor, self.executor)
        self.assertEqual(command.data, value)
        self.assertEqual(command.requests, {request})

    def test_new_command_with_arg(self):
        value = 'sccp reset SEP001122334455'
        request = Mock()

        command = self.factory.new_command(value, request, some_option=True)

        self.assertEqual(command.data, value)
        self.assertEqual(command.requests, {request})
        self.assertEqual(command.options, {'some_option': True})

    def test_new_command_unauthorized(self):
        value = 'foobar'
        request = Mock()

        self.assertRaises(ValueError, self.factory.new_command, value, request)


class TestAsteriskCommandExecutor(unittest.TestCase):
    def setUp(self):
        self.bus_publisher = Mock(BusPublisher)
        self.executor = AsteriskCommandExecutor(self.bus_publisher)

    @patch('subprocess.run')
    def test_execute(self, mock_call):
        command = Mock(requests=[])
        mock_result = Mock()
        mock_result.returncode = 0
        mock_call.return_value = mock_result

        self.executor.execute(command, sentinel.data)

        expected_args = ['asterisk', '-rx', sentinel.data]
        mock_call.assert_called_once_with(expected_args, capture_output=True, text=True)
