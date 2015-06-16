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
import os
import subprocess

from xivo_sysconf.request_handlers.command import Command

logger = logging.getLogger(__name__)


class AsteriskCommandFactory(object):

    _COMMANDS = [
        'core reload',
        'core restart now',
        'dialplan reload',
        'sip reload',
        'moh reload',
        'iax2 reload',
        'module reload app_queue.so',
        'module reload app_meetme.so',
        'module reload features',
        'voicemail reload',
        'module reload chan_sccp.so',
    ]
    _ARG_COMMANDS = [
        'sccp reset'
    ]

    def __init__(self, asterisk_command_executor):
        self._executor = asterisk_command_executor

    def new_command(self, value):
        self._check_validity(value)
        return Command(value, self._executor, value)

    def _check_validity(self, value):
        if value in self._COMMANDS:
            return
        for arg_cmd in self._ARG_COMMANDS:
            if value.startswith(arg_cmd):
                return
        raise ValueError('unauthorized command')


class AsteriskCommandExecutor(object):

    def __init__(self):
        self._null = open(os.devnull)

    def execute(self, data):
        exit_code = subprocess.call(['asterisk', '-rx', data], stdout=self._null, close_fds=True)
        if exit_code:
            logger.error('asterisk returned non-zero status code %s', exit_code)
