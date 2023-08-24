# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logger = logging.getLogger(__name__)


class Command:
    def __init__(self, value, request, executor, data, **options):
        self.value = value
        self.executor = executor
        self.data = data
        self.optimized = False
        self.requests = {request}
        self.options = options

    def execute(self):
        if self.optimized:
            logger.debug(
                'Not executing command "%s" since it has been optimized out', self.value
            )
            return

        logger.info('Executing command "%s"', self.value)
        try:
            self.executor.execute(self, self.data, **self.options)
        except Exception:
            logger.exception(
                'Error while executing command "%s" with %s', self.value, self.executor
            )


class SimpleCommandFactory:
    def __init__(self, executor):
        self._executor = executor

    def new_command(self, value, request):
        return Command(value, request, self._executor, value)
