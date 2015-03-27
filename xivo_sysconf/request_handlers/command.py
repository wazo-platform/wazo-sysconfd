# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

logger = logging.getLogger(__name__)


class Command(object):

    def __init__(self, value, executor, data):
        self.value = value
        self.executor = executor
        self.data = data
        self.optimized = False

    def execute(self):
        if self.optimized:
            logger.debug('Not executing command %s since it has been optimized out', self.value)
            return

        logger.info('Executing %s command %s...', self.executor.name, self.value)
        try:
            self.executor.execute(self.data)
        except Exception:
            logger.exception('Error while executing %s command %s', self.executor.name, self.value)


class SimpleCommandFactory(object):

    def __init__(self, executor):
        self._executor = executor

    def new_command(self, value):
        return Command(value, self._executor, value)
