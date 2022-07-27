# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Depends
from xivo.status import Status, StatusAggregator

from .dependencies import get_status_aggregator

router = APIRouter()


@router.get('/status', status_code=200)
def get_status(status_aggregator: StatusAggregator = Depends(get_status_aggregator)):
    total_status = {'rest_api': {'status': Status.ok}}
    total_status.update(status_aggregator.status())
    return total_status
