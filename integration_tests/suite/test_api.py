# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from wazo_test_helpers import until

from .helpers.base import IntegrationTest

FASTAPI_REASON = 'Not reimplemented using FastAPI'


class TestSysconfd(IntegrationTest):

    asset = 'base'

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_dhcpd_update(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.dhcpd_update()

        assert self._command_was_called(bus_events, ['dhcpd-update', '-dr'])

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_move_voicemail(self):
        old_voicemail_directory = '/var/spool/asterisk/voicemail/mycontext/oldvoicemail'
        new_voicemail_directory = '/var/spool/asterisk/voicemail/mycontext/newvoicemail'
        self._create_directory(old_voicemail_directory)
        self._given_directory_absent(new_voicemail_directory)

        self.sysconfd.move_voicemail(
            old_mailbox='oldvoicemail',
            old_context='mycontext',
            new_mailbox='newvoicemail',
            new_context='mycontext',
        )

        assert self._directory_exists(new_voicemail_directory)

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_delete_voicemail(self):
        voicemail_directory = '/var/spool/asterisk/voicemail/mycontext/myvoicemail'
        self._create_directory(voicemail_directory)

        self.sysconfd.delete_voicemail(mailbox='myvoicemail', context='mycontext')

        assert not self._directory_exists(voicemail_directory)

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_commonconf_generate(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.commonconf_generate()

        assert self._command_was_called(bus_events, ['xivo-create-config'])

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_commonconf_apply(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.commonconf_apply()

        assert self._command_was_called(bus_events, ['xivo-update-config'])
        assert self._command_was_called(bus_events, ['xivo-monitoring-update'])

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_exec_request_handlers(self):
        asterisk_command = 'dialplan reload'
        autoprov_filename = '/etc/asterisk/pjsip.d/05-autoprov-wizard.conf'
        self._create_file(autoprov_filename, owner='root')
        asterisk_reload_bus_events = self.bus.accumulator('sysconfd.asterisk.reload.#')
        request_handlers_bus_events = self.bus.accumulator(
            'sysconfd.request_handlers.#'
        )
        command_bus_events = self.bus.accumulator('sysconfd.sentinel')
        request_context = [
            {
                'resource_type': 'meeting',
                'resource_body': {
                    'uuid': '7c104958-bf9a-4681-84ed-44af84a78627',
                },
            }
        ]
        body = {
            'ipbx': [asterisk_command],
            'chown_autoprov_config': ['something'],
            'context': request_context,
        }

        response = self.sysconfd.exec_request_handlers(body)

        def asterisk_reload_events_are_sent(request_uuid):
            assert [
                message['data']['status']
                for message in asterisk_reload_bus_events.accumulate()
                if message['name'] == 'asterisk_reload_progress'
            ] == ['starting', 'completed']
            assert all(
                message['data']['request_uuids'] == [request_uuid]
                for message in asterisk_reload_bus_events.accumulate()
                if message['name'] == 'asterisk_reload_progress'
            )

        def request_handlers_event_was_sent(request_uuid):
            assert any(
                message['data']['uuid'] == request_uuid
                for message in request_handlers_bus_events.accumulate()
                if message['name'] == 'request_handlers_progress'
            )

        assert 'request_uuid' in response

        expected_command = ['asterisk', '-rx', asterisk_command]
        assert self._command_was_called(command_bus_events, expected_command)
        assert self._file_owner(autoprov_filename) == 'asterisk'

        until.assert_(
            asterisk_reload_events_are_sent, response['request_uuid'], timeout=5
        )

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_hosts(self):
        self._given_file_absent('/etc/local/hostname')
        self._given_file_absent('/etc/local/hosts')
        bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {
            'hostname': 'wazo',
            'domain': 'example.com',
        }

        self.sysconfd.hosts(body)

        expected_command = ['hostname', '-F', '/etc/local/hostname']
        assert self._command_was_called(bus_events, expected_command)
        assert self._file_exists('/etc/local/hostname')
        assert self._file_exists('/etc/local/hosts')

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_resolv_conf(self):
        self._given_file_absent('/etc/local/resolv.conf')
        body = {
            'nameservers': ['192.168.0.1'],
            'search': ['wazo.example.com'],
        }

        self.sysconfd.resolv_conf(body)

        assert self._file_exists('/etc/local/resolv.conf')

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_ha_config(self):
        self._given_file_absent('/etc/xivo/ha.conf')
        bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {'node_type': 'master', 'remote_address': '192.168.99.99'}

        self.sysconfd.ha_config.update(body)
        result = self.sysconfd.ha_config.get()

        expected_command = ['systemctl', 'restart', 'postgresql.service']
        assert self._command_was_called(bus_events, expected_command)
        expected_command = ['xivo-manage-slave-services', 'start']
        assert self._command_was_called(bus_events, expected_command)
        assert result == body
        assert self._file_exists('/etc/xivo/ha.conf')
        assert self._file_exists('/etc/cron.d/xivo-ha-master')

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_services(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {
            'networking': 'restart',
        }

        self.sysconfd.services(body)

        expected_command = ['systemctl', 'restart', 'networking.service']
        assert self._command_was_called(bus_events, expected_command)

    def test_status(self):
        result = self.sysconfd.status()

        assert result == {'status': 'up'}

    @pytest.mark.skip(reason=FASTAPI_REASON)
    def test_xivoctl(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {
            'wazo-service': 'start',
        }

        self.sysconfd.xivoctl(body)

        assert self._command_was_called(bus_events, ['wazo-service', 'start'])

    def _create_directory(self, directory):
        self.docker_exec(['mkdir', '-p', directory], 'sysconfd')

    def _directory_exists(self, directory):
        command = ' '.join(
            ['test', '-d', directory, '&&', 'echo', 'true', '||', 'echo', 'false']
        )
        out = (
            self.docker_exec(['sh', '-c', command], 'sysconfd').strip().decode('utf-8')
        )
        if out == 'true':
            return True
        elif out == 'false':
            return False
        else:
            raise RuntimeError(f'Unknown output: "{out}"')

    def _given_directory_absent(self, directory):
        self.docker_exec(['rm', '-rf', directory], 'sysconfd')

    def _create_file(self, file_name, owner):
        command = ['install', '-D', '-o', owner, '/dev/null', file_name]
        self.docker_exec(command, 'sysconfd')

    def _given_file_absent(self, file_name):
        self.docker_exec(['rm', '-f', file_name], 'sysconfd')

    def _file_owner(self, file_name):
        return (
            self.docker_exec(['stat', '-c', '%U', file_name], 'sysconfd')
            .strip()
            .decode('utf-8')
        )

    def _file_exists(self, file_name):
        command = ' '.join(
            ['test', '-f', file_name, '&&', 'echo', 'true', '||', 'echo', 'false']
        )
        out = (
            self.docker_exec(['sh', '-c', command], 'sysconfd').strip().decode('utf-8')
        )
        if out == 'true':
            return True
        elif out == 'false':
            return False
        else:
            raise RuntimeError(f'Unknown output: "{out}"')

    def _command_was_called(self, bus_events, command):
        def poll():
            return any(
                message
                for message in bus_events.accumulate()
                if message['name'] == 'sysconfd_sentinel'
                and message['data']['command'] == command
            )

        return until.true(poll, timeout=5)
