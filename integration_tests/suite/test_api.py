# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_test_helpers import until

from .helpers.base import IntegrationTest


class TestSysconfd(IntegrationTest):

    asset = 'base'

    def test_dhcpd_update(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.dhcpd_update()

        assert(self._command_was_called(bus_events, ['dhcpd-update', '-dr']))

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

        assert(self._directory_exists(new_voicemail_directory))

    def test_delete_voicemail(self):
        voicemail_directory = '/var/spool/asterisk/voicemail/mycontext/myvoicemail'
        self._create_directory(voicemail_directory)

        self.sysconfd.delete_voicemail(mailbox='myvoicemail', context='mycontext')

        assert(not self._directory_exists(voicemail_directory))

    def test_commonconf_generate(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.commonconf_generate()

        assert(self._command_was_called(bus_events, ['xivo-create-config']))

    def test_commonconf_apply(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.commonconf_apply()

        assert(self._command_was_called(bus_events, ['xivo-update-config']))
        assert(self._command_was_called(bus_events, ['xivo-monitoring-update']))

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

        def agent_event_was_sent():
            return any(
                message for message in agent_bus_events.accumulate()
                if message['name'] == 'agent_edited'
                and message['data']['id'] == agent_id
            )

        assert(self._command_was_called(command_bus_events, ['asterisk', '-rx', asterisk_command]))
        until.true(agent_event_was_sent, timeout=5)
        assert(self._file_owner(autoprov_filename) == 'asterisk')

    def test_hosts(self):
        self._given_file_absent('/etc/local/hostname')
        self._given_file_absent('/etc/local/hosts')
        bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {
            'hostname': 'wazo',
            'domain': 'example.com',
        }

        self.sysconfd.hosts(body)

        assert(self._command_was_called(bus_events, ['hostname', '-F', '/etc/local/hostname']))
        assert(self._file_exists('/etc/local/hostname'))
        assert(self._file_exists('/etc/local/hosts'))

    def test_resolv_conf(self):
        self._given_file_absent('/etc/local/resolv.conf')
        body = {
            'nameservers': ['192.168.0.1'],
            'search': ['wazo.example.com'],
        }

        self.sysconfd.resolv_conf(body)

        assert(self._file_exists('/etc/local/resolv.conf'))

    def test_ha_config(self):
        self._given_file_absent('/etc/xivo/ha.conf')
        bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {
            'node_type': 'master',
            'remote_address': '192.168.99.99'
        }

        self.sysconfd.ha_config.update(body)
        result = self.sysconfd.ha_config.get()

        assert(self._command_was_called(bus_events, ['systemctl', 'restart', 'postgresql.service']))
        assert(self._command_was_called(bus_events, ['xivo-manage-slave-services', 'start']))
        assert(result == body)
        assert(self._file_exists('/etc/xivo/ha.conf'))
        assert(self._file_exists('/etc/cron.d/xivo-ha-master'))

    def test_services(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {
            'networking': 'restart',
        }

        self.sysconfd.services(body)

        assert(self._command_was_called(bus_events, ['systemctl', 'restart', 'networking.service']))

    def test_status_check(self):
        result = self.sysconfd.status_check()

        assert(result == {'status': 'up'})

    def test_xivoctl(self):
        bus_events = self.bus.accumulator('sysconfd.sentinel')
        body = {
            'wazo-service': 'start',
        }

        self.sysconfd.xivoctl(body)

        assert(self._command_was_called(bus_events, ['wazo-service', 'start']))

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

    def _given_directory_absent(self, directory):
        self.docker_exec(['rm', '-rf', directory], 'sysconfd')

    def _create_file(self, file_name, owner):
        self.docker_exec(['install', '-D', '-o', owner, '/dev/null', file_name], 'sysconfd')

    def _given_file_absent(self, file_name):
        self.docker_exec(['rm', '-f', file_name], 'sysconfd')

    def _file_owner(self, file_name):
        return self.docker_exec(['stat', '-c', '%U', file_name], 'sysconfd').strip().decode('utf-8')

    def _file_exists(self, file_name):
        command = ' '.join(['test', '-f', file_name, '&&', 'echo', 'true', '||', 'echo', 'false'])
        out = self.docker_exec(['sh', '-c', command], 'sysconfd').strip().decode('utf-8')
        if out == 'true':
            return True
        elif out == 'false':
            return False
        else:
            raise RuntimeError(f'Unknown output: "{out}"')

    def _command_was_called(self, bus_events, command):
        def poll():
            return any(
                message for message in bus_events.accumulate()
                if message['name'] == 'sysconfd_sentinel'
                and message['data']['command'] == command
            )
        return until.true(poll, timeout=5)
