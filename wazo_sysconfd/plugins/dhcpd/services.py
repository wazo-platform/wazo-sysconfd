# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess

DHCPD_UDPATE_COMMAND = ['dhcpd-update', '-dr']


def exec_dhcp_update():
    return subprocess.call(DHCPD_UDPATE_COMMAND, close_fds=True)
