# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

config = None


@lru_cache
def get_config():
    return config
