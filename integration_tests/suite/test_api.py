# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    calling,
    contains_string,
    has_properties,
    has_items,
    has_entries,
)
from wazo_test_helpers import until
from wazo_test_helpers.hamcrest.raises import raises
from wazo_sysconfd_client.exceptions import SysconfdError

from .helpers.base import IntegrationTest

FASTAPI_REASON = 'Not reimplemented using FastAPI'


class TestSysconfd(IntegrationTest):
    asset = 'base'

    def test_dhcpd_update(self):
        bus_events = self.bus.accumulator(headers={'name': 'sysconfd_sentinel'})

        self.sysconfd.dhcpd_update()

        self._assert_command_was_called(bus_events, ['dhcpd-update', '-dr'])

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

    def test_delete_voicemail_path_injection(self):
        assert_that(
            calling(self.sysconfd.delete_voicemail).with_args(
                mailbox='../../../attack/me', context='some-context'
            ),
            raises(SysconfdError).matching(
                has_properties(status_code=400, message=contains_string('mailbox'))
            ),
        )

    def test_delete_voicemail(self):
        voicemail_directory = '/var/spool/asterisk/voicemail/mycontext/myvoicemail'
        self._create_directory(voicemail_directory)

        self.sysconfd.delete_voicemail(mailbox='myvoicemail', context='mycontext')

        assert not self._directory_exists(voicemail_directory)

    def test_commonconf_generate(self):
        bus_events = self.bus.accumulator(headers={'name': 'sysconfd_sentinel'})

        self.sysconfd.commonconf_generate()

        self._assert_command_was_called(bus_events, ['xivo-create-config'])

    def test_commonconf_apply(self):
        bus_events = self.bus.accumulator(headers={'name': 'sysconfd_sentinel'})

        self.sysconfd.commonconf_apply()

        self._assert_command_was_called(bus_events, ['xivo-update-config'])
        self._assert_command_was_called(bus_events, ['xivo-monitoring-update'])

    def test_exec_request_handlers(self):
        asterisk_command = 'dialplan reload'
        autoprov_filename = '/etc/asterisk/pjsip.d/05-autoprov-wizard.conf'
        self._create_file(autoprov_filename, owner='root')
        asterisk_accumulator = self.bus.accumulator(
            headers={'name': 'asterisk_reload_progress'}
        )
        command_accumulator = self.bus.accumulator(
            headers={'name': 'sysconfd_sentinel'}
        )
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
            assert_that(
                asterisk_accumulator.accumulate(with_headers=True),
                has_items(
                    has_entries(
                        headers=has_entries(
                            name='asterisk_reload_progress',
                        ),
                        message=has_entries(
                            data=has_entries(
                                request_uuids=[request_uuid],
                                status='starting',
                            ),
                        ),
                    ),
                    has_entries(
                        headers=has_entries(
                            name='asterisk_reload_progress',
                        ),
                        message=has_entries(
                            data=has_entries(
                                request_uuids=[request_uuid],
                                status='completed',
                            ),
                        ),
                    ),
                ),
            )

        assert 'request_uuid' in response

        expected_command = ['asterisk', '-rx', asterisk_command]
        self._assert_command_was_called(command_accumulator, expected_command)
        assert self._file_owner(autoprov_filename) == 'asterisk'

        until.assert_(
            asterisk_reload_events_are_sent, response['request_uuid'], timeout=5
        )

    def test_hosts(self):
        self._given_file_absent('/etc/local/hostname')
        self._given_file_absent('/etc/local/hosts')
        bus_events = self.bus.accumulator(headers={'name': 'sysconfd_sentinel'})
        body = {
            'hostname': 'wazo',
            'domain': 'example.com',
        }

        self.sysconfd.hosts(body)

        expected_command = ['hostname', '-F', '/etc/local/hostname']
        self._assert_command_was_called(bus_events, expected_command)
        assert self._file_exists('/etc/local/hostname')
        assert self._file_exists('/etc/local/hosts')

    def test_resolv_conf(self):
        self._given_file_absent('/etc/local/resolv.conf')
        body = {
            'nameservers': ['192.168.0.1'],
            'search': ['wazo.example.com'],
        }

        self.sysconfd.resolv_conf(body)

        assert self._file_exists('/etc/local/resolv.conf')

    def test_ha_config(self):
        self._given_file_absent('/etc/xivo/ha.conf')
        bus_events = self.bus.accumulator(headers={'name': 'sysconfd_sentinel'})
        body = {'node_type': 'master', 'remote_address': '192.168.99.99'}

        self.sysconfd.ha_config.update(body)
        result = self.sysconfd.ha_config.get()

        expected_command = ['systemctl', 'restart', 'postgresql.service']
        self._assert_command_was_called(bus_events, expected_command)
        expected_command = ['xivo-manage-slave-services', 'start']
        self._assert_command_was_called(bus_events, expected_command)
        assert result == body
        assert self._file_exists('/etc/xivo/ha.conf')
        assert self._file_exists('/etc/cron.d/xivo-ha-master')

    def test_services(self):
        bus_events = self.bus.accumulator(headers={'name': 'sysconfd_sentinel'})
        body = {
            'networking': 'restart',
        }

        self.sysconfd.services(body)

        expected_command = ['systemctl', 'restart', 'networking.service']
        self._assert_command_was_called(bus_events, expected_command)

    def test_status(self):
        result = self.sysconfd.status()

        assert result == {'rest_api': {'status': 'ok'}}

    def test_xivoctl(self):
        bus_events = self.bus.accumulator(headers={'name': 'sysconfd_sentinel'})
        body = {
            'wazo-service': 'start',
        }

        self.sysconfd.xivoctl(body)

        self._assert_command_was_called(bus_events, ['wazo-service', 'start'])

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

    def _assert_command_was_called(self, bus_events, command):
        def poll():
            assert_that(
                bus_events.accumulate(with_headers=True),
                has_items(
                    has_entries(
                        headers=has_entries(
                            name='sysconfd_sentinel', origin_uuid='sentinel-uuid'
                        ),
                        message=has_entries(data=has_entries(command=command)),
                    )
                ),
            )

        return until.assert_(poll, timeout=5)
