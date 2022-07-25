# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter
import subprocess

from wazo_sysconfd.exceptions import HttpReqError

router = APIRouter()


DHCPD_UDPATE_COMMAND = ['dhcpd-update', '-dr']


@router.get('/dhcpd_update', status_code=200)
def get_dhcp_update():
    """Download the latest ISC dhcp server configuration files and
    regenerate the affected configuration files via the dhcpd-update
    command.

    """
    try:
        returncode = subprocess.call(DHCPD_UDPATE_COMMAND, close_fds=True)
    except OSError as e:
        raise HttpReqError(500, "error while executing dhcpd-update command: %s" % e)
    else:
        if returncode:
            raise HttpReqError(500, "dhcpd-update command returned %s" % returncode)
