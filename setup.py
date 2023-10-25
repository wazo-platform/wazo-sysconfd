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
    install_requires=[
        "xivo_bus@https://github.com/wazo-platform/xivo-bus/archive/master.zip",
        "xivo@https://github.com/wazo-platform/xivo-lib-python/archive/master.zip",
        "fastapi==0.65.1",
        "gunicorn==20.1.0",
        "httptools==0.1.1",
        "kombu==5.0.2",
        "pydantic==1.7.4",
        "pyyaml==5.3.1",
        "requests==2.25.1",
        "starlette==0.14.2",
        "stevedore==3.2.2",
        "uvicorn==0.13.3",
        "uvloop==0.17.0",
    ],
    extras_require={
        'tests': ['pyhamcrest', 'pytest'],
    },
    entry_points={
        'console_scripts': [
            'wazo-sysconfd=wazo_sysconfd.main:main',
        ],
        'wazo_sysconfd.plugins': [
            'asterisk = wazo_sysconfd.plugins.asterisk.plugin:Plugin',
            'commonconf = wazo_sysconfd.plugins.commonconf.plugin:Plugin',
            'dhcp_update = wazo_sysconfd.plugins.dhcp_update.plugin:Plugin',
            'ha_config = wazo_sysconfd.plugins.ha_config.plugin:Plugin',
            'host_services = wazo_sysconfd.plugins.host_services.plugin:Plugin',
            'hosts = wazo_sysconfd.plugins.hosts.plugin:Plugin',
            'request_handlers = wazo_sysconfd.plugins.request_handlers.plugin:Plugin',
            'resolv_conf = wazo_sysconfd.plugins.resolv_conf.plugin:Plugin',
            'status = wazo_sysconfd.plugins.status.plugin:Plugin',
            'xivoctl = wazo_sysconfd.plugins.xivoctl.plugin:Plugin',
            'networking_info = wazo_sysconfd.plugins.networking_info.plugin:Plugin',
        ],
    },
)
