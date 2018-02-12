# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
import subprocess

from xivo_sysconf.request_handlers.command import SimpleCommandFactory

logger = logging.getLogger(__name__)

AuthKeysCommandFactory = SimpleCommandFactory


class AuthKeysCommandExecutor(object):

    def execute(self, data):
        exit_code = subprocess.call(['xivo-update-keys'])
        if exit_code:
            logger.error('xivo-update-keys returned non-zero status code %s', exit_code)
