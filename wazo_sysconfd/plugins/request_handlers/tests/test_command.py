# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from uuid import uuid4

from unittest.mock import Mock

from wazo_sysconfd.plugins.request_handlers.command import Command, SimpleCommandFactory


class TestCommand(unittest.TestCase):
    def setUp(self):
        self.value = Mock()
        self.request = Mock()
        self.executor = Mock()
        self.data = Mock()
        self.wazo_uuid = str(uuid4())
        self.command = Command(self.value, self.request, self.executor, self.data, self.wazo_uuid)

    def test_execute(self):
        self.command.execute()

        self.executor.execute.assert_called_once_with(self.command, self.data)

    def test_execute_catch_executor_exception(self):
        self.executor.execute.side_effect = Exception()

        self.command.execute()

        self.executor.execute.assert_called_once_with(self.command, self.data)

    def test_execute_optimized(self):
        self.command.optimized = True

        self.command.execute()

        self.assertFalse(self.executor.execute.called)


class TestSimpleCommandFactory(unittest.TestCase):
    def setUp(self):
        self.executor = Mock()
        self.factory = SimpleCommandFactory(self.executor)
        self.wazo_uuid = str(uuid4())

    def test_new_command(self):
        value = 'foobar'
        request = Mock()

        command = self.factory.new_command(value, request, self.wazo_uuid)

        self.assertEqual(command.value, value)
        self.assertIs(command.executor, self.executor)
        self.assertEqual(command.data, value)
        self.assertEqual(command.requests, {request})
