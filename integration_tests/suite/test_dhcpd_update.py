# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from xivo_test_helpers import until

from .helpers.base import IntegrationTest


class TestSysconfd(IntegrationTest):

    asset = 'base'

    def test_dhcpd_update(self):
        host = 'localhost'
        port = self.service_port(8668, 'sysconfd')
        self.sysconfd = SysconfdPublisher(f'http://{host}:{port}')
        bus_events = self.bus.accumulator('sysconfd.sentinel')

        self.sysconfd.dhcpd_update()
        self.sysconfd.flush()

        def command_was_called(command):
            print(bus_events.accumulate())
            return any(
                message for message in bus_events.accumulate()
                if message['name'] == 'sysconfd_sentinel'
                and message['data']['command'] == command
            )

        until.true(command_was_called, ['dhcpd-update', '-dr'], timeout=5)


class SysconfdError(Exception):
    def __init__(self, code, value):
        self.code = code
        self.value = value

    def __str__(self):
        return "sysconfd error: status {} - {}".format(self.code, self.value)


class SysconfdPublisher:
    def __init__(self, base_url):
        self.base_url = base_url
        self._reset()

    def exec_request_handlers(self, args):
        self.add_handlers(args)

    def add_handlers(self, args):
        for service, new_commands in args.items():
            commands = self.handlers.setdefault(service, set())
            commands.update(set(new_commands))

    def move_voicemail(self, old_number, old_context, number, context):
        params = {
            'old_mailbox': old_number,
            'old_context': old_context,
            'new_mailbox': number,
            'new_context': context,
        }
        url = "{}/move_voicemail".format(self.base_url)
        self.add_request('GET', url, params=params)

    def delete_voicemail(self, number, context):
        params = {'mailbox': number, 'context': context}
        url = "{}/delete_voicemail".format(self.base_url)
        self.add_request('GET', url, params=params)

    def commonconf_apply(self):
        url = "{}/commonconf_apply".format(self.base_url)
        self.add_request('GET', url)

    def commonconf_generate(self):
        url = "{}/commonconf_generate".format(self.base_url)
        self.add_request('POST', url, json={})

    def set_hosts(self, hostname, domain):
        data = {'hostname': hostname, 'domain': domain}
        url = "{}/hosts".format(self.base_url)
        self.add_request('POST', url, json=data)

    def set_resolvconf(self, nameserver, domain):
        data = {'nameservers': nameserver, 'search': [domain]}
        url = "{}/resolv_conf".format(self.base_url)
        self.add_request('POST', url, json=data)
        self.flush()

    def service_action(self, service_name, action):
        data = {service_name: action}
        url = "{}/services".format(self.base_url)
        self.add_request('POST', url, json=data)

    def restart_provd(self):
        self.service_action('wazo-provd', 'restart')

    def restart_phoned(self):
        self.service_action('wazo-phoned', 'restart')

    def dhcpd_update(self):
        url = "{}/dhcpd_update".format(self.base_url)
        self.add_request('GET', url)

    def xivo_service_start(self):
        data = {'wazo-service': 'start'}
        url = "{}/xivoctl".format(self.base_url)
        self.add_request('POST', url, json=data)

    def xivo_service_enable(self):
        data = {'wazo-service': 'enable'}
        url = "{}/xivoctl".format(self.base_url)
        self.add_request('POST', url, json=data)

    def get_ha_config(self):
        session = self._session()
        url = "{}/get_ha_config".format(self.base_url)
        return session.get(url).json()

    def update_ha_config(self, ha):
        url = "{}/update_ha_config".format(self.base_url)
        self.add_request('POST', url, json=ha)

    def _session(self):
        session = requests.Session()
        session.trust_env = False
        return session

    def check_for_errors(self, response):
        if response.status_code != 200:
            raise SysconfdError(response.status_code, response.text)

    def add_request(self, *args, **kwargs):
        self.requests.append(lambda session: session.request(*args, **kwargs))

    def flush(self):
        session = self._session()
        self.flush_handlers(session)
        self.flush_requests(session)
        self._reset()

    def flush_handlers(self, session):
        if len(self.handlers) > 0:
            url = "{}/exec_request_handlers".format(self.base_url)
            body = {key: tuple(commands) for key, commands in self.handlers.items()}
            response = session.request('POST', url, json=body)
            self.check_for_errors(response)

    def flush_requests(self, session):
        for request_applicator in self.requests:
            response = request_applicator(session)
            self.check_for_errors(response)

    def rollback(self):
        self._reset()

    def _reset(self):
        self.requests = []
        self.handlers = {}
