# Copyright 2015-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import subprocess
import time
import uuid

import requests
from wazo_bus.resources.sysconfd.event import AsteriskReloadProgressEvent

from wazo_sysconfd.plugins.request_handlers.command import Command

MAX_ATTEMPTS = 10
RELOAD_IN_PROGRESS_MSG = 'Another reload is currently in progress'

logger = logging.getLogger(__name__)

# accepted CLI reload commands and their ARI module name
ARI_RELOAD_MODULES = {
    'dialplan reload': 'pbx_config',
    'moh reload': 'res_musiconhold',
    'iax2 reload': 'chan_iax2',
    'voicemail reload': 'app_voicemail',
    'module reload app_queue.so': 'app_queue',
    'module reload features': 'features',
    'module reload res_parking.so': 'res_parking',
    'module reload res_pjsip.so': 'res_pjsip',
    'module reload chan_sccp.so': 'chan_sccp',
    'module reload app_confbridge.so': 'app_confbridge',
    'module reload res_rtp_asterisk.so': 'res_rtp_asterisk',
    'module reload res_hep.so': 'res_hep',
}


class AsteriskCommandFactory:
    def __init__(self, asterisk_command_executor):
        self._executor = asterisk_command_executor

    def new_command(self, value, request, **options):
        self._check_validity(value)
        return Command(value, request, self._executor, value, **options)

    def _check_validity(self, value):
        if value not in ARI_RELOAD_MODULES:
            raise ValueError('unauthorized command')


class AsteriskCommandExecutor:
    def __init__(self, bus_publisher, ari_config):
        self._bus_publisher = bus_publisher
        self._ari_config = ari_config
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

        self._try_reload_module(ARI_RELOAD_MODULES[command_string])

        if publish:
            self.publish_status(task_uuid, 'completed', command_string, request_uuids)

    def _try_reload_module(self, module: str, attempt: int = 1):
        url = '{base_url}/ari/asterisk/modules/{module}'.format(
            base_url=self._ari_config['base_url'], module=module
        )
        auth = (self._ari_config['username'], self._ari_config['password'])
        # asterisk executes the reload before answering, so read_timeout must
        # exceed the slowest expected reload; on timeout the reload keeps
        # running in asterisk, only the wait is abandoned
        timeout = (
            self._ari_config['connect_timeout'],
            self._ari_config['read_timeout'],
        )
        try:
            response = requests.put(url, auth=auth, timeout=timeout)
        except requests.RequestException as e:
            logger.error('Error while reloading %s through ARI: %s', module, e)
            return

        if response.status_code == 409 and RELOAD_IN_PROGRESS_MSG in response.text:
            if attempt <= MAX_ATTEMPTS:
                logger.error(
                    "Asterisk didn't actually reload. Attempt %s. Will retry.", attempt
                )
                time.sleep(1)
                self._try_reload_module(module, attempt + 1)
            else:
                logger.error(
                    "Asterisk didn't actually reload. Max retries exceeded. Giving up."
                )
        elif response.status_code == 202:
            logger.info(
                'Asterisk is not fully booted, the reload of %s has been queued',
                module,
            )
        elif response.status_code >= 400:
            logger.error(
                'Error while reloading %s through ARI: %s %s',
                module,
                response.status_code,
                response.text,
            )
        else:
            logger.debug('Asterisk module %s reloaded', module)

    def publish_status(
        self, task_uuid: str, status: str, command: str, request_uuids: list
    ) -> None:
        self._bus_publisher.publish(
            AsteriskReloadProgressEvent(task_uuid, status, command, request_uuids)
        )
