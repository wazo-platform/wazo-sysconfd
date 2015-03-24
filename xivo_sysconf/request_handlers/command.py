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
        self._value = value
        self._executor = executor
        self._data = data

    def execute(self):
        logger.info('Executing %s command %s...', self._executor.name, self._value)
        try:
            self._executor.execute(self._data)
        except Exception:
            logger.exception('Error while executing %s command %s', self._executor.name, self._value)


class SimpleCommandFactory(object):

    def __init__(self, executor):
        self._executor = executor

    def new_command(self, value):
        return Command(value, self._executor, value)
