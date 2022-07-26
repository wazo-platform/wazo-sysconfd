# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock
from wazo_sysconfd.plugins.request_handlers.command import Command, SimpleCommandFactory


class TestCommand(unittest.TestCase):

    def setUp(self):
        self.value = Mock()
        self.request = Mock()
        self.executor = Mock()
        self.data = Mock()
        self.command = Command(self.value, self.request, self.executor, self.data)

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

    def test_new_command(self):
        value = 'foobar'
        request = Mock()

        command = self.factory.new_command(value, request)

        self.assertEqual(command.value, value)
        self.assertIs(command.executor, self.executor)
        self.assertEqual(command.data, value)
        self.assertEqual(command.requests, {request})
