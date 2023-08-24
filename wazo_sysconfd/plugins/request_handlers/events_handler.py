# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_sysconfd.bus import BusConsumerProxy
from xivo_bus.resources.sysconfd.event import AsteriskReloadProgressEvent

from .dependencies import get_request_handlers_proxy


class EventHandler:
    def __init__(self, wazo_uuid: str, bus_consumer: BusConsumerProxy):
        self.uuid = wazo_uuid
        self.bus = bus_consumer

    def subscribe(self):
        subscriptions = ((AsteriskReloadProgressEvent.name, self._on_asterisk_reload),)

        for event_name, callback in subscriptions:
            self.bus.subscribe(event_name, callback)

    def _on_asterisk_reload(self, event: dict, headers: dict) -> None:
        request_handlers_proxy = get_request_handlers_proxy()

        if event['status'] != 'starting':
            return

        # only execute handlers if event originated from another WAZO
        if (origin_uuid := headers.get('origin_uuid')) and origin_uuid != self.uuid:
            request_handlers_proxy.handle_request(event, {'publish': False})
