# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from xivo_test_helpers.bus import BusClient
from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase


class IntegrationTest(AssetLaunchingTestCase):

    assets_root = os.path.join(os.path.dirname(__file__), '../..', 'assets')
    service = 'sysconfd'

    def setUp(self):
        bus_port = self.service_port(5672, 'rabbitmq')
        self.bus = BusClient.from_connection_fields(host='localhost', port=bus_port)
