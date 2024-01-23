# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter

from .services import get_system_network_interfaces

router = APIRouter()


@router.get('/networking/interfaces', status_code=200)
def get_networking_interfaces():
    """
    Query the system's network interfaces
    """
    return {'data': list(get_system_network_interfaces())}
