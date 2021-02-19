# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from xivo_test_helpers import until

from .helpers.base import IntegrationTest


class TestSysconfd(IntegrationTest):

    asset = 'base'

    def test_dhcpd_update(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.dhcpd_update()

        def command_was_called(command):
            return any(
                message for message in bus_events.accumulate()
                if message['name'] == 'sysconfd_sentinel'
                and message['data']['command'] == command
            )

        until.true(command_was_called, ['dhcpd-update', '-dr'], timeout=5)

    def test_delete_voicemail(self):
        voicemail_directory = '/var/spool/asterisk/voicemail/mycontext/myvoicemail'
        self._create_directory(voicemail_directory)

        self.sysconfd.delete_voicemail(mailbox='myvoicemail', context='mycontext')

        assert(not self._directory_exists(voicemail_directory))

    def _create_directory(self, directory):
        self.docker_exec(['mkdir', '-p', directory], 'sysconfd')

    def _directory_exists(self, directory):
        command = ' '.join(['test', '-d', directory, '&&', 'echo', 'true', '||', 'echo', 'false'])
        out = self.docker_exec(['sh', '-c', command], 'sysconfd').strip().decode('utf-8')
        if out == 'true':
            return True
        elif out == 'false':
            return False
        else:
            raise RuntimeError(f'Unknown output: "{out}"')
