# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from mock import Mock, sentinel
from xivo_sysconf.request_handlers.command import Command
from xivo_sysconf.request_handlers.request import Request, RequestFactory, \
    DuplicateRequestOptimizer, RequestQueue, RequestProcessor, RequestHandlers,\
    SyncRequestHandlers, SyncRequestObserver
from xivo.http_json_server import HttpReqError


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
        self.cti_command_factory = Mock()
        self.dird_command_factory = Mock()
        self.agent_command_factory = Mock()
        self.request_factory = RequestFactory(self.asterisk_command_factory,
                                              self.cti_command_factory,
                                              self.dird_command_factory,
                                              self.agent_command_factory)

    def test_new_request_ipbx(self):
        args = {
            'ipbx': ['foo'],
        }

        request = self.request_factory.new_request(args)

        self.asterisk_command_factory.new_command.assert_called_once_with('foo')
        self.assertEqual(request.commands, [self.asterisk_command_factory.new_command.return_value])

    def test_new_request_ctibus(self):
        args = {
            'ctibus': ['foo'],
        }

        request = self.request_factory.new_request(args)

        self.cti_command_factory.new_command.assert_called_once_with('foo')
        self.assertEqual(request.commands, [self.cti_command_factory.new_command.return_value])

    def test_new_request_dird(self):
        args = {
            'dird': ['foo'],
        }

        request = self.request_factory.new_request(args)

        self.dird_command_factory.new_command.assert_called_once_with('foo')
        self.assertEqual(request.commands, [self.dird_command_factory.new_command.return_value])

    def test_new_request_agentbus(self):
        args = {
            'agentbus': ['foo'],
        }

        request = self.request_factory.new_request(args)

        self.agent_command_factory.new_command.assert_called_once_with('foo')
        self.assertEqual(request.commands, [self.agent_command_factory.new_command.return_value])

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
        cmd1 = self._new_command('a')
        cmd2 = self._new_command('a')

        self.optimizer.on_request_put(Request([cmd1]))

        self.assertFalse(cmd1.optimized)

        self.optimizer.on_request_put(Request([cmd2]))

        self.assertFalse(cmd1.optimized)
        self.assertTrue(cmd2.optimized)

    def test_on_request_put_same_commands_different_executor(self):
        cmd1 = self._new_command('a')
        cmd2 = self._new_command('a', self.other_executor)

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
        cmd1 = self._new_command('a')
        cmd2 = self._new_command('a')
        cmd3 = self._new_command('a')

        self.optimizer.on_request_put(Request([cmd1]))
        self.optimizer.on_request_put(Request([cmd2]))

        self.assertFalse(cmd1.optimized)
        self.assertTrue(cmd2.optimized)

        self.optimizer.on_request_get(Request([cmd1]))
        self.optimizer.on_request_put(Request([cmd3]))

        self.assertFalse(cmd3.optimized)

    def _new_command(self, value, executor=None):
        if executor is None:
            executor = self.executor
        return Command(value, executor, value)


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


class TestExit(BaseException):
    pass


class TestRequestProcessor(unittest.TestCase):

    def setUp(self):
        self.request_queue = Mock()
        self.request_processor = RequestProcessor(self.request_queue)

    def test_run(self):
        request = self.request_queue.get.return_value
        request.execute.side_effect = TestExit()

        try:
            self.request_processor.run()
        except TestExit:
            pass


class TestRequestHandlers(unittest.TestCase):

    def setUp(self):
        self.request_factory = Mock()
        self.request_queue = Mock()
        self.request_handlers = RequestHandlers(self.request_factory, self.request_queue)

    def test_handle_request(self):
        self.request_handlers.handle_request(sentinel.args, None)

        self.request_factory.new_request.assert_called_once_with(sentinel.args)
        self.request_queue.put.assert_called_once_with(self.request_factory.new_request.return_value)

    def test_handle_request_invalid(self):
        self.request_factory.new_request.side_effect = Exception()

        self.assertRaises(HttpReqError, self.request_handlers.handle_request, sentinel.args, None)


class TestSyncRequestObserver(unittest.TestCase):

    def test_without_timeout(self):
        observer = SyncRequestObserver()
        observer.on_request_executed()
        self.assertTrue(observer.wait())

    def test_with_timeout(self):
        observer = SyncRequestObserver(0.1)
        self.assertFalse(observer.wait())


class TestSyncRequestHandlers(unittest.TestCase):

    def setUp(self):
        self.request_factory = Mock()
        self.request_queue = Mock()
        self.request_queue.put.side_effect = self._request_queue_put
        self.request_handlers = SyncRequestHandlers(self.request_factory, self.request_queue)

    def _request_queue_put(self, request):
        request.observer.on_request_executed()

    def test_handle_request(self):
        self.request_handlers.handle_request(sentinel.args, None)

        self.request_queue.put.assert_called_once_with(self.request_factory.new_request.return_value)
