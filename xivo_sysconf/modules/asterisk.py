# -*- coding: utf-8 -*-

# Copyright (C) 2011-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os.path
import shutil
import subprocess

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_R

ASTERISK_USER = 'asterisk'
ASTERISK_GROUP = 'asterisk'


class Asterisk(object):

    def __init__(self, base_vmail_path='/var/spool/asterisk/voicemail'):
        self._base_vmail_path = base_vmail_path
        self.remove_directory = _remove_directory
        self.move_directory = _move_directory
        self.is_valid_path_component = _is_valid_path_component

    def delete_voicemail(self, args, options):
        if 'mailbox' not in options:
            raise HttpReqError(400, "missing 'mailbox' arg", json=True)

        context = options.get('context', 'default')
        mailbox = options['mailbox']

        if not self.is_valid_path_component(context):
            raise HttpReqError(400, 'invalid context')
        if not self.is_valid_path_component(mailbox):
            raise HttpReqError(400, 'invalid mailbox')

        vmpath = os.path.join(self._base_vmail_path, context, mailbox)
        self.remove_directory(vmpath)

        return True

    def move_voicemail(self, args, options):
        self._validate_options(options)

        old_path = os.path.join(self._base_vmail_path,
                                options['old_context'],
                                options['old_mailbox'])
        new_path = os.path.join(self._base_vmail_path,
                                options['new_context'],
                                options['new_mailbox'])

        self.move_directory(old_path, new_path)

        return True

    def _validate_options(self, options):
        for param in ('old_context', 'old_mailbox', 'new_context', 'new_mailbox'):
            value = options.get(param)
            if not value:
                raise HttpReqError(400, "missing '{}' arg".format(param),
                                   json=True)
            if not self.is_valid_path_component(value):
                raise HttpReqError(400, 'invalid {}'.format(param))


def _remove_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def _move_directory(old_path, new_path):
    dirname = os.path.dirname(new_path)
    commands = [
        ["rm", "-rf", new_path],
        ["install", "-d", "-m", "750", "-o", ASTERISK_USER, "-g", ASTERISK_GROUP, dirname],
        ["mv", old_path, new_path]
    ]

    for cmd in commands:
        subprocess.check_call(cmd)


def _is_valid_path_component(path_component):
    return bool(path_component and
                path_component != os.curdir and
                path_component != os.pardir and
                os.sep not in path_component)


def core_show_version(args, options):
    command = 'core show version'
    return _exec_asterisk_command(command)


def core_show_channels(args, options):
    command = 'core show channels'
    return _exec_asterisk_command(command)


def sip_show_peer(args, options):
    peer = options.get('peer')
    if not peer:
        raise HttpReqError(400, 'missing peer')

    command = 'sip show peer {}'.format(peer)
    return _exec_asterisk_command(command)


def _exec_asterisk_command(command):
    p = subprocess.Popen(['asterisk', '-rx', command],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)
    output = p.communicate()[0]

    if p.returncode != 0:
        raise HttpReqError(500, output)
    return output


asterisk = Asterisk()
http_json_server.register(asterisk.delete_voicemail, CMD_R,
                          name='delete_voicemail')
http_json_server.register(asterisk.move_voicemail, CMD_R,
                          name='move_voicemail')
http_json_server.register(core_show_version, CMD_R,
                          name='core_show_version')
http_json_server.register(core_show_channels, CMD_R,
                          name='core_show_channels')
http_json_server.register(sip_show_peer, CMD_R,
                          name='sip_show_peer')
