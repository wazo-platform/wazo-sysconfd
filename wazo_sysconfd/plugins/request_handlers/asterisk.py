# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import subprocess
import uuid

from wazo_sysconfd.plugins.request_handlers.command import Command
from xivo_bus.resources.sysconfd.event import AsteriskReloadProgressEvent

RELOAD_IN_PROGRESS_MSG = (
    'A module reload request is already in progress; please be patient\n'
)

logger = logging.getLogger(__name__)


class AsteriskCommandFactory:
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

    def new_command(self, value, request, **options):
        self._check_validity(value)
        return Command(value, request, self._executor, value, **options)

    def _check_validity(self, value):
        if value in self._COMMANDS:
            return
        for arg_cmd in self._ARG_COMMANDS:
            if value.startswith(arg_cmd):
                return
        raise ValueError('unauthorized command')


class AsteriskCommandExecutor:
    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher
        self._null = open(os.devnull)

    def execute(self, command: Command, data, *, publish: bool = True):
        command_string = data
        request_uuids = [request.uuid for request in command.requests]
        task_uuid = str(uuid.uuid4())

        if publish:
            self.publish_status(task_uuid, 'starting', command_string, request_uuids)

        if command_string == 'module reload res_pjsip.so':
            cmd = ['wazo-confgen', 'asterisk/pjsip.conf', '--invalidate']
            subprocess.call(cmd, stdout=self._null, close_fds=True)

        result = subprocess.run(
            ['asterisk', '-rx', command_string], capture_output=True, text=True
        )
        if result.returncode:
            logger.error('asterisk returned non-zero status code %s', result.returncode)
        if result.stdout == RELOAD_IN_PROGRESS_MSG:
            logger.error("asterisk didn't actually reload")

        if publish:
            self.publish_status(task_uuid, 'completed', command_string, request_uuids)

    def publish_status(
        self, task_uuid: str, status: str, command: str, request_uuids: list
    ) -> None:
        self._bus_publisher.publish(
            AsteriskReloadProgressEvent(task_uuid, status, command, request_uuids)
        )
