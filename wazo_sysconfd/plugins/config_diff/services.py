# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import logging

from fastapi import HTTPException
from git import Repo
from git.exc import GitCommandError

from .dependencies import get_config
from .models import ConfigHistoryDiff, ConfigHistoryLog, ConfigHistoryLogItem

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
    commits = list(repo.iter_commits(after=start_date, before=end_date))
    try:
        patch_str = repo.git.diff(commits[0], commits[-1])
    except GitCommandError as e:
        logger.error(f"AFDEBUG: Error getting config diff by date range: {e.stderr}")
        raise HTTPException(
            status_code=400,
            detail=f"Error getting config diff by date range: {e.stderr}",
        )
    return ConfigHistoryDiff(item=patch_str)


def get_config_diff_by_commit(commit_a: str, commit_b: str) -> ConfigHistoryDiff:
    repo = Repo(get_config()['repo_path'])
    try:
        patch_str = repo.git.diff(commit_a, commit_b)
    except GitCommandError as e:
        logger.error(f"AFDEBUG: Error getting config diff by commit: {e.stderr}")
        raise HTTPException(
            status_code=400, detail=f"Error getting config diff by commit: {e.stderr}"
        )
    return ConfigHistoryDiff(item=patch_str)
