# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logger = logging.getLogger(__name__)


class Command(object):

    def __init__(self, value, request, executor, data):
        self.value = value
        self.executor = executor
        self.data = data
        self.optimized = False
        self.requests = {request}

    def execute(self):
        if self.optimized:
            logger.debug('Not executing command "%s" since it has been optimized out', self.value)
            return

        logger.info('Executing command "%s"', self.value)
        try:
            self.executor.execute(self, self.data)
        except Exception:
            logger.exception('Error while executing command "%s" with %s', self.value, self.executor)


class SimpleCommandFactory(object):

    def __init__(self, executor):
        self._executor = executor

    def new_command(self, value, request):
        return Command(value, request, self._executor, value)
