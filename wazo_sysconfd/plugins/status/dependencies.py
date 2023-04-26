# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

status_aggregator = None


@lru_cache
def get_status_aggregator():
    return status_aggregator
