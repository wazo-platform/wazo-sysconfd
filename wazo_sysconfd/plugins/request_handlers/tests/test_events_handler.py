# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock, patch

from wazo_sysconfd.bus import BusConsumer
from wazo_sysconfd.plugins.request_handlers.events_handler import EventHandler
from wazo_sysconfd.plugins.request_handlers.request import RequestHandlersProxy


class TestEventHandler(unittest.TestCase):
    def setUp(self):
        self.handler_patcher = patch(
            'wazo_sysconfd.plugins.request_handlers.events_handler.get_request_handlers_proxy',
            new_callable=Mock(return_value=Mock(RequestHandlersProxy)),
        )

        self.get_handlers_proxy = self.handler_patcher.start()
        self.wazo_uuid = wazo_uuid = str(uuid4())
        self.consumer = consumer = Mock(BusConsumer)
        self.event_handler = EventHandler(wazo_uuid, consumer)

    def tearDown(self):
        self.handler_patcher.stop()

    def test_subscribe(self):
        self.event_handler.subscribe()

        self.consumer.subscribe.assert_called_once_with(
            'asterisk_reload_progress',
            self.event_handler._on_asterisk_reload,
        )

    def test_on_asterisk_reload_progress_completed(self):
        event = {
            'status': 'completed',
        }
        headers = {
            'name': 'asterisk_reload_progress',
            'origin_uuid': str(uuid4()),
        }

        self.event_handler._on_asterisk_reload(event, headers)

        self.get_handlers_proxy().handle_request.assert_not_called()

    def test_on_asterisk_reload_progress_from_same_wazo(self):
        event = {
            'status': 'starting',
        }
        headers = {
            'name': 'asterisk_reload_progress',
            'origin_uuid': self.wazo_uuid,
        }

        self.event_handler._on_asterisk_reload(event, headers)

        self.get_handlers_proxy().handle_request.assert_not_called()

    def test_on_asterisk_reload_progress_executing(self):
        command = 'module reload res_pjsip.so'
        event = {
            'status': 'starting',
            'command': command,
            'request_uuids': [str(uuid4())],
        }
        headers = {
            'name': 'asterisk_reload_progress',
            'origin_uuid': str(uuid4()),
        }

        self.event_handler._on_asterisk_reload(event, headers)

        expected_payload = {
            'ipbx': [event['command']],
            'request_uuids': event['request_uuids'],
        }
        self.get_handlers_proxy().handle_request.assert_called_once_with(
            expected_payload, {'publish': False}
        )
