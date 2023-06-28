# Copyright 2010-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo_sysconfd',
    version='2.0',
    description='Wazo sysconf daemon',
    author='Wazo Authors',
    author_email='dev@wazo.io',
    url='https://wazo-platform.org',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'wazo-sysconfd=wazo_sysconfd.main:main',
        ],
        'wazo_sysconfd.plugins': [
            'commonconf = wazo_sysconfd.plugins.commonconf.plugin:Plugin',
            'dhcpd = wazo_sysconfd.plugins.dhcpd.plugin:Plugin',
            'ha = wazo_sysconfd.plugins.ha.plugin:Plugin',
            'hosts = wazo_sysconfd.plugins.hosts.plugin:Plugin',
            'request_handlers = wazo_sysconfd.plugins.request_handlers.plugin:Plugin',
            'resolv_conf = wazo_sysconfd.plugins.resolv_conf.plugin:Plugin',
            'services = wazo_sysconfd.plugins.services.plugin:Plugin',
            'status = wazo_sysconfd.plugins.status.plugin:Plugin',
            'networking_info = wazo_sysconfd.plugins.networking_info.plugin:Plugin',
            'voicemail = wazo_sysconfd.plugins.voicemail.plugin:Plugin',
            'wazoctl = wazo_sysconfd.plugins.wazoctl.plugin:Plugin',
        ],
    },
)
