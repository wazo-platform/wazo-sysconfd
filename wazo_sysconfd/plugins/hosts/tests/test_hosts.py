# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    calling,
    not_,
    raises,
)

from wazo_sysconfd.modules.resolvconf import (
    HttpReqError,
    _validate_hosts as validate_hosts,
)

class TestValidateHosts(unittest.TestCase):
    
    def test_domain(self):
        invalid_names = [
            64 * 'a.wazo-platform.org',
            '-NOT',
            'NOT-',
            'foo!bar',
            'foo.-NOT.bar',
        ]

        for name in invalid_names:
            body = {'domain': name, 'hostname': 'valid'}

            assert_that(
                calling(validate_hosts).with_args(body),
                raises(HttpReqError),
                name,
            )

        body = {'domain': 'a' * 63 + '.wazo-platform.org', 'hostname': 'valid'}

        assert_that(
            calling(validate_hosts).with_args(body),
            not_(raises(HttpReqError)),
        )

    def test_hostname(self):
        invalid_names = [
            64 * 'a',
            '-NOT',
            'NOT-',
            'foo!bar',
        ]

        for name in invalid_names:
            body = {'domain': 'valid', 'hostname': name}

            assert_that(
                calling(validate_hosts).with_args(body),
                raises(HttpReqError),
                name,
            )

        body = {'domain': 'valid', 'hostname': 'foo-bar'}

        assert_that(
            calling(validate_hosts).with_args(body),
            not_(raises(HttpReqError)),
        )
