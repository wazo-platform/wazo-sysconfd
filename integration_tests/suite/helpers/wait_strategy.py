# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries, has_entry
from requests.exceptions import RequestException
from wazo_test_helpers import until


class WaitStrategy:
    def wait(self, integration_test):
        raise NotImplementedError()


class EverythingOkWaitStrategy(WaitStrategy):
    def wait(self, integration_test):
        def is_ready():
            try:
                status = integration_test.sysconfd.status()
            except RequestException:
                status = {}
            assert_that(
                status,
                has_entries(
                    rest_api=has_entry('status', 'ok'),
                    bus_consumer=has_entry('status', 'ok'),
                ),
            )

        until.assert_(is_ready, tries=30)
