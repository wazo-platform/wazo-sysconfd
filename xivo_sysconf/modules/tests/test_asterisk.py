# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import os
import shutil
import tempfile
import unittest
from mock import Mock, call
from xivo.http_json_server import HttpReqError
from xivo_sysconf.modules.asterisk import Asterisk, _remove_directory, _is_valid_path_component


class TestAsterisk(unittest.TestCase):

    def setUp(self):
        self.base_voicemail_path = '/tmp/foo/bar'
        self.remove_directory = Mock()
        self.is_valid_path_component = Mock()
        self.asterisk = Asterisk(self.base_voicemail_path)
        self.asterisk.remove_directory = self.remove_directory
        self.asterisk.is_valid_path_component = self.is_valid_path_component

    def test_delete_voicemail(self):
        self.is_valid_path_component.return_value = True
        context = 'foo'
        voicemail_id = '100'
        options = {'context': context, 'name': voicemail_id}

        self.asterisk.delete_voicemail(None, options)

        self.assertEqual([call(context), call(voicemail_id)],
                         self.is_valid_path_component.call_args_list)
        expected_path = os.path.join(self.base_voicemail_path, context, voicemail_id)
        self.remove_directory.assert_called_once_with(expected_path)

    def test_invalid_path_component_raise_error(self):
        self.asterisk.is_valid_path_component.return_value = False
        options = {'context': '', 'name': ''}

        self.assertRaises(HttpReqError, self.asterisk.delete_voicemail, None, options)


class TestRemoveDirectory(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def test_remove(self):
        _remove_directory(self.path)

        self.assertFalse(os.path.exists(self.path))


class TestPathComponentValidator(unittest.TestCase):

    def test_valid_path_component(self):
        path_components = [
            'foo',
            'foo.bar',
            '1234',
        ]

        for pc in path_components:
            self.assertTrue(_is_valid_path_component(pc), pc)

    def test_invalid_path_component(self):
        path_components = [
            '.',
            '..',
            'foo/bar',
            '',
        ]

        for pc in path_components:
            self.assertFalse(_is_valid_path_component(pc), pc)
