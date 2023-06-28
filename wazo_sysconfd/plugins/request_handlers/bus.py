# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from fastapi import Depends

from wazo_sysconfd.bus import BusConsumer

from .dependencies import get_request_handlers_proxy
from .request import RequestHandlersProxy


class EventHandler:
    def __init__(self):
        self._wazo_uuid = os.getenv('XIVO_UUID')

    def subscribe(self, bus_consumer: BusConsumer):
        bus_consumer.subscribe('asterisk_reload_progress', self._on_asterisk_reload_progress)

    def _on_asterisk_reload_progress(
        self,
        event: dict,
        request_handlers_proxy: RequestHandlersProxy = Depends(get_request_handlers_proxy),
    ):
        if event['status'] != 'starting':
            return

        from_wazo_uuid = event.get('from_wazo_uuid')
        if not from_wazo_uuid:
            return

        if from_wazo_uuid == self._wazo_uuid:
            return

        return request_handlers_proxy.handle_request(event, None)
