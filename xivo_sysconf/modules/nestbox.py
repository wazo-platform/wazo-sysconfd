# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os
import subprocess

from xivo import http_json_server
from xivo.http_json_server import CMD_R


class NestboxDependenciesInstaller(object):

    def remove_nestbox_dependencies(self, args, options):
        for package in ('wazo-nestbox-plugin', 'wazo-deployd-client'):
            if os.path.exists("/var/lib/dpkg/info/{}.md5sums".format(package)):
                command_args = ['/usr/bin/apt-get', 'purge', '-y', package]
                subprocess.check_call(command_args, close_fds=True)


nestbox_dependencies_installer = NestboxDependenciesInstaller()
http_json_server.register(nestbox_dependencies_installer.remove_nestbox_dependencies, CMD_R,
                          name='remove_nestbox_dependencies')
