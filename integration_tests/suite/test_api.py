# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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

    def test_commonconf_generate(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.commonconf_generate()

        def command_was_called(command):
            return any(
                message for message in bus_events.accumulate()
                if message['name'] == 'sysconfd_sentinel'
                and message['data']['command'] == command
            )

        until.true(command_was_called, ['xivo-create-config'], timeout=5)

    def test_commonconf_apply(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.commonconf_apply()

        def command_was_called(command):
            return any(
                message for message in bus_events.accumulate()
                if message['name'] == 'sysconfd_sentinel'
                and message['data']['command'] == command
            )

        until.true(command_was_called, ['xivo-update-config'], timeout=5)
        until.true(command_was_called, ['xivo-monitoring-update'], timeout=5)

    def test_exec_request_handlers(self):
        agent_id = 12
        asterisk_command = 'dialplan reload'
        autoprov_filename = '/etc/asterisk/pjsip.d/05-autoprov-wizard.conf'
        self._create_file(autoprov_filename, owner='root')
        agent_bus_events = self.bus.accumulator('config.agent.edited')
        command_bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {
            'ipbx': [asterisk_command],
            'agentbus': [f'agent.edit.{agent_id}'],
            'chown_autoprov_config': ['something'],
        }

        self.sysconfd.exec_request_handlers(body)

        def command_was_called(command):
            return any(
                message for message in command_bus_events.accumulate()
                if message['name'] == 'sysconfd_sentinel'
                and message['data']['command'] == command
            )

        def agent_event_was_sent():
            return any(
                message for message in agent_bus_events.accumulate()
                if message['name'] == 'agent_edited'
                and message['data']['id'] == agent_id
            )

        until.true(command_was_called, ['asterisk', '-rx', asterisk_command], timeout=5)
        until.true(agent_event_was_sent, timeout=5)
        assert(self._file_owner(autoprov_filename) == 'asterisk')

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

    def _create_file(self, file_name, owner):
        self.docker_exec(['install', '-D', '-o', owner, '/dev/null', file_name], 'sysconfd')

    def _file_owner(self, file_name):
        return self.docker_exec(['stat', '-c', '%U', file_name], 'sysconfd').strip().decode('utf-8')
