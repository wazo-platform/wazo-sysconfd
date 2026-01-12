# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime

from pydantic import BaseModel


class ConfigHistoryLogItem(BaseModel):
    commit: str
    date: datetime.datetime
    files_changed: list[str]


class ConfigHistoryLog(BaseModel):
    items: list[ConfigHistoryLogItem]


class ConfigHistoryDiff(BaseModel):
    item: str
