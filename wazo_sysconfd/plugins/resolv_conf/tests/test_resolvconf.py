# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, calling, not_, raises

from wazo_sysconfd import exceptions
from wazo_sysconfd.plugins.resolv_conf.services import (
    _validate_resolv_conf as validate_resolv_conf,
)


class TestValidateResolvConf(unittest.TestCase):
    def test_nameservers(self):
        assert_that(
            calling(validate_resolv_conf).with_args({}),
            raises(exceptions.HttpReqError),
        )

        assert_that(
            calling(validate_resolv_conf).with_args({'nameservers': []}),
            raises(exceptions.HttpReqError),
        )

        assert_that(
            calling(validate_resolv_conf).with_args(
                {'nameservers': ['10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4']},
            ),
            raises(exceptions.HttpReqError),
        )

        invalid_ip_or_domain = [
            '-foo.wazo-platform.org',
            None,
            'a' * 64,
            '127.0.0.-1',
        ]

        for ip_or_domain in invalid_ip_or_domain:
            assert_that(
                calling(validate_resolv_conf).with_args(
                    {'nameservers': [ip_or_domain]},
                ),
                raises(exceptions.HttpReqError),
                ip_or_domain,
            )

    def test_search(self):
        assert_that(
            calling(validate_resolv_conf).with_args(
                {'nameservers': ['valid'], 'search': []}
            ),
            raises(exceptions.HttpReqError),
        )

        assert_that(
            calling(validate_resolv_conf).with_args(
                {
                    'nameservers': ['valid'],
                    'search': [
                        'toto.1.tld',
                        'toto.2.tld',
                        'toto.3.tld',
                        'toto.4.tld',
                        'toto.5.tld',
                        'toto.6.tld',
                        'toto.7.tld',
                    ],
                },
            ),
            raises(exceptions.HttpReqError),
        )

        invalid_names = [
            64 * 'a' + '.wazo-platform.org',
            '-NOT',
            'NOT-',
            'foo!bar',
            'foo.-NOT.bar',
        ]

        for name in invalid_names:
            body = {
                'nameservers': ['valid'],
                'search': [name],
            }
            assert_that(
                calling(validate_resolv_conf).with_args(body),
                raises(exceptions.HttpReqError),
                name,
            )

        valid_body = {'nameservers': ['valid'], 'search': ['valid']}
        assert_that(
            calling(validate_resolv_conf).with_args(valid_body),
            not_(raises(Exception)),
        )
