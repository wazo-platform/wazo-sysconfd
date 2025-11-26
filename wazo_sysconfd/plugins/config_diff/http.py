# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

from fastapi import APIRouter, HTTPException

from . import services
from .models import ConfigHistoryDiff, ConfigHistoryLog

router = APIRouter()


@router.get('/config-history', status_code=200)
def get_config_history() -> ConfigHistoryLog:
    config_history = services.get_config_history_list()
    return config_history


@router.get('/config-history/diff', status_code=200)
def get_config_history_diff(
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
    commit_a: str | None = None,
    commit_b: str | None = None,
) -> ConfigHistoryDiff:
    if start_date or end_date:
        config_diff = services.get_config_diff_by_date_range(start_date, end_date)
    elif commit_a and commit_b:
        config_diff = services.get_config_diff_by_commit(commit_a, commit_b)
    else:
        raise HTTPException(status_code=400, detail="Invalid request")
    return config_diff
