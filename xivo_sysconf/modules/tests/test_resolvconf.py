# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    calling,
    not_,
    raises,
)

from ..resolvconf import (
    HttpReqError,
    _validate_hosts as validate_hosts,
    _validate_resolv_conf as validate_resolv_conf,
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


class TestValidateResolvConf(unittest.TestCase):

    def test_nameservers(self):
        assert_that(
            calling(validate_resolv_conf).with_args({}),
            raises(HttpReqError),
        )

        assert_that(
            calling(validate_resolv_conf).with_args({'nameservers': []}),
            raises(HttpReqError),
        )

        assert_that(
            calling(validate_resolv_conf).with_args(
                {'nameservers': ['10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4']},
            ),
            raises(HttpReqError),
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
                raises(HttpReqError),
                ip_or_domain,
            )

    def test_search(self):
        assert_that(
            calling(validate_resolv_conf).with_args({'nameservers': ['valid'], 'search': []}),
            raises(HttpReqError),
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
            raises(HttpReqError),
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
                raises(HttpReqError),
                name,
            )
