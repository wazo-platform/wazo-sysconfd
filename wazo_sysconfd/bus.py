# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.status import Status

from xivo_bus.consumer import BusConsumer as Consumer


class BusConsumer(Consumer):
    @classmethod
    def from_config(cls, bus_config):
        return cls(name='wazo-sysconfd', **bus_config)

    def provide_status(self, status):
        status['bus_consumer']['status'] = (
            Status.ok if self.consumer_connected() else Status.fail
        )
