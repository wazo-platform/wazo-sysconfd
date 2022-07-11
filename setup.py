# Copyright 2010-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo_sysconfd',
    version='2.0',
    description='Wazo sysconf daemon',
    author='Wazo Authors',
    author_email='dev.wazo@gmail.com',
    url='https://wazo-platform.org',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'wazo-sysconfd=wazo_sysconfd.main:main',
        ],
        'wazo_sysconfd.plugins': [
            'asterisk = wazo_sysconfd.plugins.asterisk.plugin:Plugin',
            'commonconf = wazo_sysconfd.plugins.commonconf.plugin:Plugin',
            'dhcp_update = wazo_sysconfd.plugins.dhcp_update.plugin:Plugin',
            'ha_config = wazo_sysconfd.plugins.ha_config.plugin:Plugin',
            'hosts = wazo_sysconfd.plugins.hosts.plugin:Plugin',
            'request_handlers = wazo_sysconfd.plugins.request_handlers.plugin:Plugin',
            'services = wazo_sysconfd.plugins.services.plugin:Plugin',
            'status = wazo_sysconfd.plugins.status.plugin:Plugin',
            'xivoctl = wazo_sysconfd.plugins.xivoctl.plugin:Plugin',
        ],
    },
)
