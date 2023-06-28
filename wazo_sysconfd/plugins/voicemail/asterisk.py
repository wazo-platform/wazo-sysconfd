# Copyright 2011-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os.path
import shutil
import subprocess

from wazo_sysconfd.exceptions import HttpReqError

ASTERISK_USER = 'asterisk'
ASTERISK_GROUP = 'asterisk'


class Asterisk:
    def __init__(self, base_vmail_path='/var/spool/asterisk/voicemail'):
        self._base_vmail_path = base_vmail_path
        self.remove_directory = _remove_directory
        self.move_directory = _move_directory
        self.is_valid_path_component = _is_valid_path_component

    def delete_voicemail(self, context, mailbox):
        if not mailbox:
            raise HttpReqError(400, "missing 'mailbox' arg")

        if not self.is_valid_path_component(context):
            raise HttpReqError(400, 'invalid context')
        if not self.is_valid_path_component(mailbox):
            raise HttpReqError(400, 'invalid mailbox')

        vmpath = os.path.join(self._base_vmail_path, context, mailbox)
        self.remove_directory(vmpath)

    def move_voicemail(
        self,
        old_context,
        old_mailbox,
        new_context,
        new_mailbox,
    ):
        self._validate_option('old_context', old_context)
        self._validate_option('old_mailbox', old_mailbox)
        self._validate_option('new_context', new_context)
        self._validate_option('new_mailbox', new_mailbox)

        old_path = os.path.join(self._base_vmail_path, old_context, old_mailbox)
        new_path = os.path.join(self._base_vmail_path, new_context, new_mailbox)

        self.move_directory(old_path, new_path)

    def _validate_option(self, name, value):
        if not value:
            raise HttpReqError(400, f"missing '{name}' arg")
        if not self.is_valid_path_component(value):
            raise HttpReqError(400, f'invalid {value}')


def _remove_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def _move_directory(old_path, new_path):
    if not os.path.exists(old_path):
        return

    dirname = os.path.dirname(new_path)
    commands = [
        ["rm", "-rf", new_path],
        [
            "install",
            "-d",
            "-m",
            "750",
            "-o",
            ASTERISK_USER,
            "-g",
            ASTERISK_GROUP,
            dirname,
        ],
        ["mv", old_path, new_path],
    ]

    for cmd in commands:
        subprocess.check_call(cmd)


def _is_valid_path_component(path_component):
    return bool(
        path_component
        and path_component != os.curdir
        and path_component != os.pardir
        and os.sep not in path_component
    )
