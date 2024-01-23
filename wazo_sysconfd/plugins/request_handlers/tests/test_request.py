# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import ANY, Mock, sentinel

from wazo_sysconfd.plugin_helpers.exceptions import HttpReqError
from wazo_sysconfd.plugins.request_handlers.command import Command
from wazo_sysconfd.plugins.request_handlers.request import (
    DuplicateRequestOptimizer,
    Request,
    RequestFactory,
    RequestHandlers,
    RequestProcessor,
    RequestQueue,
    SyncRequestHandlers,
    SyncRequestObserver,
)


class TestRequest(unittest.TestCase):
    def test_execute(self):
        command1 = Mock()
        command2 = Mock()
        commands = [command1, command2]
        request = Request(commands)

        request.execute()

        command1.execute.assert_called_once_with()
        command2.execute.assert_called_once_with()

    def test_execute_with_observer(self):
        request = Request([])
        request.observer = Mock()

        request.execute()

        request.observer.on_request_executed()


class TestRequestFactory(unittest.TestCase):
    def setUp(self):
        self.asterisk_command_factory = Mock()
        self.chown_autoprov_config_command_factory = Mock()
        self.request_factory = RequestFactory(
            self.asterisk_command_factory, self.chown_autoprov_config_command_factory
        )

    def test_new_request_ipbx(self):
        args = {
            'ipbx': ['foo'],
        }

        request = self.request_factory.new_request(args)

        self.asterisk_command_factory.new_command.assert_called_once_with('foo', ANY)
        self.assertEqual(
            request.commands, [self.asterisk_command_factory.new_command.return_value]
        )

    def test_new_request_chown_autoprov(self):
        args = {
            'chown_autoprov_config': ['foo'],
        }

        request = self.request_factory.new_request(args)
        self.chown_autoprov_config_command_factory.new_command.assert_called_once_with(
            'foo', ANY
        )
        self.assertEqual(
            request.commands,
            [self.chown_autoprov_config_command_factory.new_command.return_value],
        )

    def test_new_request_invalid_command(self):
        returns = [ValueError(), sentinel.command]
        args = {
            'ipbx': ['1', '2'],
        }

        def side_effect(*args):
            result = returns.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        self.asterisk_command_factory.new_command.side_effect = side_effect

        request = self.request_factory.new_request(args)

        self.assertEqual(request.commands, [sentinel.command])


class TestDuplicateRequestOptimizer(unittest.TestCase):
    def setUp(self):
        self.executor = Mock()
        self.other_executor = Mock()
        self.optimizer = DuplicateRequestOptimizer(self.executor)

    def test_on_request_put_same_commands(self):
        request1 = Request([])
        request2 = Request([])
        cmd1 = self._new_command('a', request1)
        cmd2 = self._new_command('a', request2)
        request1.commands = [cmd1]
        request2.commands = [cmd2]

        self.optimizer.on_request_put(request1)

        self.assertFalse(cmd1.optimized)

        self.optimizer.on_request_put(request2)

        self.assertFalse(cmd1.optimized)
        self.assertTrue(cmd2.optimized)
        assert cmd1.requests == {request1, request2}

    def test_on_request_put_same_commands_different_executor(self):
        cmd1 = self._new_command('a')
        cmd2 = self._new_command('a', executor=self.other_executor)

        self.optimizer.on_request_put(Request([cmd1, cmd2]))

        self.assertFalse(cmd1.optimized)
        self.assertFalse(cmd2.optimized)

    def test_on_request_put_different_commands(self):
        cmd1 = self._new_command('a')
        cmd2 = self._new_command('b')

        self.optimizer.on_request_put(Request([cmd1, cmd2]))

        self.assertFalse(cmd1.optimized)
        self.assertFalse(cmd2.optimized)

    def test_on_request_put_after_get(self):
        request1 = Request([])
        request2 = Request([])
        request3 = Request([])
        cmd1 = self._new_command('a', request1)
        cmd2 = self._new_command('a', request2)
        cmd3 = self._new_command('a', request3)
        request1.commands = [cmd1]
        request2.commands = [cmd2]
        request3.commands = [cmd3]

        self.optimizer.on_request_put(request1)
        self.optimizer.on_request_put(request2)

        self.assertFalse(cmd1.optimized)
        self.assertTrue(cmd2.optimized)
        assert cmd1.requests == {request1, request2}

        self.optimizer.on_request_get(request1)
        self.optimizer.on_request_put(request3)

        self.assertFalse(cmd3.optimized)
        assert cmd3.requests == {request3}

    def _new_command(self, value, request=None, executor=None):
        if executor is None:
            executor = self.executor
        return Command(value, request, executor, value)

    def _new_request_from_command(self, command):
        request = Request()
        return request.commands


class TestRequestQueue(unittest.TestCase):
    def setUp(self):
        self.optimizer = Mock()
        self.request_queue = RequestQueue(self.optimizer)

    def test_put_and_get(self):
        self.request_queue.put(sentinel.request)

        self.optimizer.on_request_put.assert_called_once_with(sentinel.request)

        request = self.request_queue.get()

        self.assertEqual(request, sentinel.request)
        self.optimizer.on_request_get.assert_called_once_with(sentinel.request)


class ExitTestException(BaseException):
    pass


class TestRequestProcessor(unittest.TestCase):
    def setUp(self):
        self.request_queue = Mock()
        self.request_processor = RequestProcessor(self.request_queue)

    def test_run(self):
        request = self.request_queue.get.return_value
        request.execute.side_effect = ExitTestException()

        try:
            self.request_processor.run()
        except ExitTestException:
            pass


class TestRequestHandlers(unittest.TestCase):
    def setUp(self):
        self.bus_publisher = Mock()
        self.request_factory = Mock()
        self.request_queue = Mock()
        self.request_handlers = RequestHandlers(
            self.request_factory, self.request_queue, self.bus_publisher
        )

    def test_handle_request(self):
        self.request_handlers.handle_request(sentinel.args, None)

        self.request_factory.new_request.assert_called_once_with(sentinel.args)
        self.request_queue.put.assert_called_once_with(
            self.request_factory.new_request.return_value
        )

    def test_handle_request_invalid(self):
        self.request_factory.new_request.side_effect = Exception()

        self.assertRaises(
            HttpReqError, self.request_handlers.handle_request, sentinel.args, None
        )


class TestSyncRequestObserver(unittest.TestCase):
    def test_without_timeout(self):
        request = Mock()
        observer = SyncRequestObserver()
        observer.on_request_executed(request)
        self.assertTrue(observer.wait())

    def test_with_timeout(self):
        observer = SyncRequestObserver(0.1)
        self.assertFalse(observer.wait())


class TestSyncRequestHandlers(unittest.TestCase):
    def setUp(self):
        self.bus_publisher = Mock()
        self.request_factory = Mock()
        self.request_factory.new_request.return_value = Mock(observers=[])
        self.request_queue = Mock()
        self.request_queue.put.side_effect = self._request_queue_put
        self.request_handlers = SyncRequestHandlers(
            self.request_factory, self.request_queue, self.bus_publisher
        )

    def _request_queue_put(self, request):
        for observer in request.observers:
            observer.on_request_executed(request)

    def test_handle_request(self):
        self.request_handlers.handle_request(sentinel.args, None)

        self.request_queue.put.assert_called_once_with(
            self.request_factory.new_request.return_value
        )
