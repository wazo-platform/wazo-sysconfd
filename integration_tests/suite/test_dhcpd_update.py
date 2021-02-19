# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from xivo_test_helpers import until
from wazo_sysconfd_client.client import SysconfdClient

from .helpers.base import IntegrationTest


class TestSysconfd(IntegrationTest):

    asset = 'base'

    def test_dhcpd_update(self):
        host = 'localhost'
        port = self.service_port(8668, 'sysconfd')
        self.sysconfd = SysconfdClient(host, port, prefix='', https=False)
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.dhcpd_update()

        def command_was_called(command):
            print(bus_events.accumulate())
            return any(
                message for message in bus_events.accumulate()
                if message['name'] == 'sysconfd_sentinel'
                and message['data']['command'] == command
            )

        until.true(command_was_called, ['dhcpd-update', '-dr'], timeout=5)
