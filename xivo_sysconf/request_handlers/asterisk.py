# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import os
import subprocess
import uuid

from xivo_bus.resources.asterisk.event import AsteriskReloadProgressEvent

from .command import Command

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
        'module reload res_parking.so',
        'voicemail reload',
        'module reload chan_sccp.so',
        'module reload app_confbridge.so',
        'module reload res_rtp_asterisk.so',
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

    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher
        self._null = open(os.devnull)

    def execute(self, data):
        task_uuid = str(uuid.uuid4())
        self._bus_publisher.publish(
            AsteriskReloadProgressEvent(uuid=task_uuid, status='starting', command=data)
        )

        exit_code = subprocess.call(['asterisk', '-rx', data], stdout=self._null, close_fds=True)
        if exit_code:
            logger.error('asterisk returned non-zero status code %s', exit_code)

        self._bus_publisher.publish(
            AsteriskReloadProgressEvent(uuid=task_uuid, status='completed', command=data)
        )
