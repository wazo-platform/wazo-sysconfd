# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import logging

from . import services
from fastapi import APIRouter

from .models import ConfigHistoryDiff, ConfigHistoryLog

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/config-history', status_code=200)
def get_config_history() -> ConfigHistoryLog:
    config_history = services.get_config_history_list()
    return config_history


@router.get('/config-history/diff', status_code=200)
def get_config_history_diff(
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None
) -> ConfigHistoryDiff:
    logger.debug(f"AFDEBUG: start_date: {start_date} end_date: {end_date}")
    config_diff = services.get_config_diff_by_date_range(start_date, end_date)
    return config_diff
