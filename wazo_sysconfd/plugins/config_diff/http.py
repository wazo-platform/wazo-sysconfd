# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

from . import services
from fastapi import APIRouter

from .models import ConfigHistoryDiff, ConfigHistoryLog

router = APIRouter()


@router.get('/config-history', status_code=200)
def get_config_history() -> ConfigHistoryLog:
    config_history = services.get_config_history_list()
    return config_history


@router.get('/config-history/diff', status_code=200)
def get_config_history_diff(
    date_start: datetime.datetime | None, date_end: datetime.datetime | None
) -> ConfigHistoryDiff:
    config_diff = services.get_config_diff_by_date_range(date_start, date_end)
    return config_diff
