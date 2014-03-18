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
from xivo_sysconf.modules.asterisk import Asterisk


class TestAsterisk(unittest.TestCase):
    def setUp(self):
        self._base_voicemail_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._base_voicemail_path)

    def _make_voicemail_path(self, context, voicemail_id):
        voicemail_path = os.path.join(self._base_voicemail_path, context,
                                      voicemail_id)
        os.makedirs(voicemail_path)
        return voicemail_path

    def test_delete_voicemail_deletes_voicemail_path(self):
        context = 'foo'
        voicemail_id = '100'
        voicemail_path = self._make_voicemail_path(context, voicemail_id)

        asterisk_obj = Asterisk(self._base_voicemail_path)
        asterisk_obj.delete_voicemail(None, {'context': context, 'name': voicemail_id})

        self.assertFalse(os.path.exists(voicemail_path))
