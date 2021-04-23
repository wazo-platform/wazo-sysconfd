# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from wazo_sysconfd_client.client import SysconfdClient
from xivo_test_helpers.bus import BusClient
from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase


class IntegrationTest(AssetLaunchingTestCase):

    assets_root = os.path.join(os.path.dirname(__file__), '../..', 'assets')
    service = 'sysconfd'

    def setUp(self):
        bus_port = self.service_port(5672, 'rabbitmq')
        self.bus = BusClient.from_connection_fields(host='127.0.0.1', port=bus_port)

        sysconfd_port = self.service_port(8668, 'sysconfd')
        self.sysconfd = SysconfdClient(
            '127.0.0.1',
            sysconfd_port,
            prefix='',
            https=False,
        )
