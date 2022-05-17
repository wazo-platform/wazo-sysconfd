# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from xivo.status import StatusAggregator

router = APIRouter()


@router.get('/status', status_code=200)
def get_status(status: StatusAggregator = Depends(StatusAggregator)):
    total_status = {'status': 'up'}
    if status is not None:
        total_status.update(status.status())

    return total_status
