# Copyright 2023-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.sysconfd.event import AsteriskReloadProgressEvent

from wazo_sysconfd.bus import BusConsumerProxy

from .dependencies import get_request_handlers_proxy


class EventHandler:
    def __init__(self, wazo_uuid: str, bus_consumer: BusConsumerProxy):
        self.uuid = wazo_uuid
        self.bus = bus_consumer

    def subscribe(self):
        self.bus.subscribe(AsteriskReloadProgressEvent.name, self._on_asterisk_reload)

    def _on_asterisk_reload(self, event: dict, headers: dict) -> None:
        if event['status'] != 'starting':
            return

        # only execute handlers if event originated from another WAZO
        if (origin_uuid := headers.get('origin_uuid')) and origin_uuid != self.uuid:
            payload = {
                'ipbx': [event['command']],
                'request_uuids': event['request_uuids'],
            }
            request_handlers_proxy = get_request_handlers_proxy()
            request_handlers_proxy.handle_request(payload, {'publish': False})
