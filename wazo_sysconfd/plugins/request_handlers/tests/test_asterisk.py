# Copyright 2015-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

import requests
from wazo_bus import BusPublisher

from wazo_sysconfd.plugins.request_handlers.asterisk import (
    MAX_ATTEMPTS,
    AsteriskCommandExecutor,
    AsteriskCommandFactory,
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

    def test_new_command_with_option(self):
        value = 'dialplan reload'
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
        self.ari_config = {
            'base_url': 'http://localhost:5039',
            'username': 'xivo',
            'password': 'secret',
            'connect_timeout': 5,
            'read_timeout': 60,
        }
        self.executor = AsteriskCommandExecutor(self.bus_publisher, self.ari_config)

    def _new_response(self, status_code, text=''):
        return Mock(status_code=status_code, text=text)

    @patch('wazo_sysconfd.plugins.request_handlers.asterisk.requests.put')
    def test_execute_reloads_module_through_ari(self, mock_put):
        command = Mock(requests=[])
        mock_put.return_value = self._new_response(204)

        self.executor.execute(command, 'dialplan reload')

        mock_put.assert_called_once_with(
            'http://localhost:5039/ari/asterisk/modules/pbx_config',
            auth=('xivo', 'secret'),
            timeout=(5, 60),
        )

    @patch('subprocess.call')
    @patch('wazo_sysconfd.plugins.request_handlers.asterisk.requests.put')
    def test_execute_pjsip_invalidates_confgen_cache(self, mock_put, mock_call):
        command = Mock(requests=[])
        mock_put.return_value = self._new_response(204)

        self.executor.execute(command, 'module reload res_pjsip.so')

        expected_args = ['wazo-confgen', 'asterisk/pjsip.conf', '--invalidate']
        self.assertEqual(mock_call.call_args[0][0], expected_args)
        self.assertIn('res_pjsip', mock_put.call_args[0][0])

    @patch('time.sleep')
    @patch('wazo_sysconfd.plugins.request_handlers.asterisk.requests.put')
    def test_execute_retries_when_reload_in_progress(self, mock_put, mock_sleep):
        command = Mock(requests=[])
        in_progress = self._new_response(
            409, '{"message": "Another reload is currently in progress"}'
        )
        mock_put.side_effect = [in_progress, self._new_response(204)]

        self.executor.execute(command, 'dialplan reload')

        self.assertEqual(mock_put.call_count, 2)

    @patch('time.sleep')
    @patch('wazo_sysconfd.plugins.request_handlers.asterisk.requests.put')
    def test_execute_gives_up_after_max_attempts(self, mock_put, mock_sleep):
        command = Mock(requests=[])
        in_progress = self._new_response(
            409, '{"message": "Another reload is currently in progress"}'
        )
        mock_put.return_value = in_progress

        self.executor.execute(command, 'dialplan reload')

        self.assertEqual(mock_put.call_count, MAX_ATTEMPTS + 1)

    @patch('time.sleep')
    @patch('wazo_sysconfd.plugins.request_handlers.asterisk.requests.put')
    def test_execute_does_not_retry_other_conflicts(self, mock_put, mock_sleep):
        command = Mock(requests=[])
        mock_put.return_value = self._new_response(
            409, '{"message": "Module does not support reloading"}'
        )

        self.executor.execute(command, 'dialplan reload')

        mock_put.assert_called_once()
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    @patch('wazo_sysconfd.plugins.request_handlers.asterisk.requests.put')
    def test_execute_accepts_queued_reload(self, mock_put, mock_sleep):
        command = Mock(requests=[])
        mock_put.return_value = self._new_response(202)

        self.executor.execute(command, 'dialplan reload')

        mock_put.assert_called_once()
        mock_sleep.assert_not_called()

    @patch('wazo_sysconfd.plugins.request_handlers.asterisk.requests.put')
    def test_execute_still_publishes_completed_on_connection_error(self, mock_put):
        command = Mock(requests=[])
        mock_put.side_effect = requests.ConnectionError('asterisk is down')

        self.executor.execute(command, 'dialplan reload')

        statuses = [
            call.args[0].content['status']
            for call in self.bus_publisher.publish.call_args_list
        ]
        self.assertEqual(statuses, ['starting', 'completed'])
