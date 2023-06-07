# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os


def get_system_network_interfaces():
    interfaces = os.listdir('/sys/class/net/')
    for nic in interfaces:
        with open(f'/sys/class/net/{nic}/address') as file:
            address = file.read().strip()

        yield {'name': nic, 'address': address}
