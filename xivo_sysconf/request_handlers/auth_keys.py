# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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
import subprocess

from xivo_sysconf.request_handlers.command import SimpleCommandFactory

logger = logging.getLogger(__name__)

AuthKeysCommandFactory = SimpleCommandFactory


class AuthKeysCommandExecutor(object):

    def execute(self, data):
        exit_code = subprocess.call(['xivo-update-keys'])
        if exit_code:
            logger.error('xivo-update-keys returned non-zero status code %s', exit_code)