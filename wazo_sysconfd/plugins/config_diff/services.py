# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import logging
from git import Repo

from .dependencies import get_config
from .models import ConfigHistoryDiff,ConfigHistoryLog, ConfigHistoryLogItem

logger = logging.getLogger(__name__)


def get_config_history_list() -> ConfigHistoryLog:
    repo = Repo(get_config()['repo_path'])
    commits = repo.iter_commits()
    items = []
    for commit in commits:
        items.append(
            ConfigHistoryLogItem(
                commit=commit.hexsha,
                date=commit.committed_date,
                files_changed=list(commit.stats.files.keys()) or [],
            )
        )
    return ConfigHistoryLog(items=items)


def get_config_diff_by_date_range(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> ConfigHistoryDiff:
    repo = Repo(get_config()['repo_path'])
    params = ["-p"]
    if start_date:
        params.append("--since")
        params.append(start_date.isoformat())
    if end_date:
        params.append("--until")
        params.append(end_date.isoformat())
    patch_str = repo.git.log(*params)
    return ConfigHistoryDiff(item=patch_str)
