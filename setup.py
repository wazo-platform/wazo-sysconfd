#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='xivo_sysconfd',
    version='1.1',
    description='XIVO sysconf daemon',
    author='Proformatique',
    author_email='technique@proformatique.com',
    url='http://xivo.io/',
    packages=['xivo_sysconf',
              'xivo_sysconf.modules'],
    scripts=['bin/xivo-sysconfd']
)
