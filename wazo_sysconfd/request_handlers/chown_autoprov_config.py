# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import logging

from pwd import getpwnam

from wazo_sysconfd.request_handlers.command import SimpleCommandFactory

logger = logging.getLogger(__name__)

ChownAutoprovCommandFactory = SimpleCommandFactory


class ChownAutoprovCommandExecutor(object):

    _CONFIG_FILE = '/etc/asterisk/pjsip.d/05-autoprov-wizard.conf'

    def execute(self, command, data):
        try:
            user = getpwnam('asterisk')
        except KeyError:
            logger.warning('failed to find user asterisk')
            logger.warning('failed to create the Asterisk autoprov configuration file')
            return

        try:
            os.chown(self._CONFIG_FILE, user.pw_uid, user.pw_gid)
        except Exception as e:
            logger.info('%s', e)
            logger.warning('failed to chown autoprov configuration file %s', self._CONFIG_FILE)
