# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import subprocess
import uuid

from wazo_sysconfd.plugins.request_handlers.command import Command
from xivo_bus.resources.sysconfd.event import AsteriskReloadProgressEvent

logger = logging.getLogger(__name__)


class AsteriskCommandFactory(object):

    _COMMANDS = [
        'core reload',
        'core restart now',
        'dialplan reload',
        'moh reload',
        'iax2 reload',
        'module reload app_queue.so',
        'module reload features',
        'module reload res_parking.so',
        'module reload res_pjsip.so',
        'voicemail reload',
        'module reload chan_sccp.so',
        'module reload app_confbridge.so',
        'module reload res_rtp_asterisk.so',
        'module reload res_hep.so',
    ]
    _ARG_COMMANDS = ['sccp reset']

    def __init__(self, asterisk_command_executor):
        self._executor = asterisk_command_executor

    def new_command(self, value, request):
        self._check_validity(value)
        return Command(value, request, self._executor, value)

    def _check_validity(self, value):
        if value in self._COMMANDS:
            return
        for arg_cmd in self._ARG_COMMANDS:
            if value.startswith(arg_cmd):
                return
        raise ValueError('unauthorized command')


class AsteriskCommandExecutor(object):
    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher
        self._null = open(os.devnull)

    def execute(self, command, data):
        command_string = data
        request_uuids = [request.uuid for request in command.requests]
        task_uuid = str(uuid.uuid4())

        event = AsteriskReloadProgressEvent(
            task_uuid, 'starting', command_string, request_uuids
        )
        self._bus_publisher.publish(event)

        if command_string == 'module reload res_pjsip.so':
            cmd = ['wazo-confgen', 'asterisk/pjsip.conf', '--invalidate']
            subprocess.call(cmd, stdout=self._null, close_fds=True)

        exit_code = subprocess.call(
            ['asterisk', '-rx', command_string], stdout=self._null, close_fds=True
        )

        if exit_code:
            logger.error('asterisk returned non-zero status code %s', exit_code)

        import time
        cmd = ['pgrep', 'wazo-confgen']
        for n in range(10):
            code = subprocess.call(cmd, stdout=self._null, close_fds=True)
            reload_in_progress = not(bool(code))
            logger.critical(reload_in_progress)
            if not reload_in_progress:
                break
            time.sleep(1)

        event = AsteriskReloadProgressEvent(
            task_uuid, 'completed', command_string, request_uuids
        )
        self._bus_publisher.publish(event)
