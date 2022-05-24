# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Depends
from xivo.status import StatusAggregator

router = APIRouter()


@router.get('/status', status_code=200)
def get_status(status_aggregator: StatusAggregator = Depends(StatusAggregator)):
    total_status = {'status': 'up'}
    if status_aggregator is not None:
        total_status.update(status_aggregator.status())

    return total_status
