# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter

from wazo_sysconfd.exceptions import HttpReqError
from wazo_sysconfd.plugins.dhcp_update.services import exec_dhcp_update

router = APIRouter()


@router.get('/dhcpd_update', status_code=200)
def get_dhcp_update():
    """Download the latest ISC dhcp server configuration files and
    regenerate the affected configuration files via the dhcpd-update
    command.
    """
    try:
        returncode = exec_dhcp_update()
    except OSError as e:
        raise HttpReqError(500, f"error while executing dhcpd-update command: {e}")
    else:
        if returncode:
            raise HttpReqError(500, f"dhcpd-update command returned {returncode}")
