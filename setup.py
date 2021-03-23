#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo_sysconfd',
    version='1.2',
    description='Wazo sysconf daemon',
    author='Wazo Authors',
    author_email='dev.wazo@gmail.com',
    url='http://wazo.community',
    packages=find_packages(),
    scripts=['bin/wazo-sysconfd']
)
