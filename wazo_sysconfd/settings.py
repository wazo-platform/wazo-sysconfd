# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import lru_cache

from wazo_sysconfd.plugins.asterisk.asterisk import Asterisk


@lru_cache()
def get_asterisk():
    return Asterisk()
