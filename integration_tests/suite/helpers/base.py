# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from wazo_sysconfd_client.client import SysconfdClient
from wazo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from wazo_test_helpers.bus import BusClient

from .wait_strategy import EverythingOkWaitStrategy


class IntegrationTest(AssetLaunchingTestCase):
    assets_root = os.path.join(os.path.dirname(__file__), '../..', 'assets')
    service = 'sysconfd'
    wait_strategy = EverythingOkWaitStrategy()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bus: BusClient = cls.make_bus()
        cls.sysconfd: SysconfdClient = cls.make_sysconfd()
        cls.wait_strategy.wait(cls)

    @classmethod
    def make_bus(cls):
        port = cls.service_port(5672, 'rabbitmq')
        return BusClient.from_connection_fields(
            host='127.0.0.1',
            port=port,
            exchange_name='wazo-headers',
            exchange_type='headers',
        )

    @classmethod
    def make_sysconfd(cls):
        port = cls.service_port(8668, 'sysconfd')
        return SysconfdClient(
            '127.0.0.1',
            port,
            prefix='',
            https=False,
        )
