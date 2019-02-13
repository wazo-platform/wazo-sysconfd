# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from xivo.http_json_server import register, CMD_R, HttpReqError

DHCPD_UDPATE_COMMAND = ['dhcpd-update', '-dr']


def dhcpd_update(args, options):
    """Download the latest ISC dhcp server configuration files and
    regenerate the affected configuration files via the dhcpd-update
    command.

    """
    try:
        returncode = subprocess.call(DHCPD_UDPATE_COMMAND, close_fds=True)
    except OSError, e:
        raise HttpReqError(500, "error while executing dhcpd-update command", e)
    else:
        if returncode:
            raise HttpReqError(500, "dhcpd-update command returned %s" % returncode)
        else:
            return True


register(dhcpd_update, CMD_R, name='dhcpd_update')
