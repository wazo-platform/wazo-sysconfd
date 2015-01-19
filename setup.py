#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo_sysconfd',
    version='1.1',
    description='XIVO sysconf daemon',
    author='Proformatique',
    author_email='technique@proformatique.com',
    url='http://xivo.io/',
    packages=find_packages(),
    scripts=['bin/xivo-sysconfd']
)
