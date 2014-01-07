# -*- coding: utf-8 -*-

# Copyright (C) 2010-2014 Avencall
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

from hamcrest import assert_that, equal_to
from mock import ANY, Mock, patch, sentinel
from unittest import TestCase

from .. import services


class TestServices(TestCase):
    def setUp(self):
        services = ['service%s' % i for i in range(1, 10)]
        self.patcher = patch('os.listdir', return_value=services)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_services_should_return_empty_string_when_called_with_empty_dict(self):
        result = services.services({}, sentinel.options)

        assert_that(result, equal_to(''))

    @patch('subprocess.Popen')
    def test_services_should_call_service_action_for_each_service(self, mock_popen_constructor):
        mock_popen = mock_popen_constructor.return_value = Mock(returncode=0)
        mock_popen.communicate.return_value = ('', '')
        service1, action1 = "service1", "start"
        service2, action2 = "service2", "stop"

        services.services({service1: action1,
                           service2: action2}, sentinel.options)

        mock_popen_constructor.assert_any_call(["/etc/init.d/service1", action1], stdout=ANY, stderr=ANY, close_fds=ANY)
        mock_popen_constructor.assert_any_call(["/etc/init.d/service2", action2], stdout=ANY, stderr=ANY, close_fds=ANY)

    @patch('subprocess.Popen')
    def test_services_should_not_call_service_action_for_invalid_actions_service(self, mock_popen_constructor):
        mock_popen = mock_popen_constructor.return_value = Mock(returncode=0)
        mock_popen.communicate.return_value = ('', '')
        service1, action1 = "service1", "start"
        service2, action2 = "service2", "invalid"
        service3, action3 = "service3", "restart"
        service4, action4 = "service4", "invalid2"
        service5, action5 = "service5", "stop"

        services.services({service1: action1,
                           service2: action2,
                           service3: action3,
                           service4: action4,
                           service5: action5},
                          sentinel.options)

        mock_popen_constructor.assert_any_call(["/etc/init.d/service1", action1], stdout=ANY, stderr=ANY, close_fds=ANY)
        mock_popen_constructor.assert_any_call(["/etc/init.d/service3", action3], stdout=ANY, stderr=ANY, close_fds=ANY)
        mock_popen_constructor.assert_any_call(["/etc/init.d/service5", action5], stdout=ANY, stderr=ANY, close_fds=ANY)
        assert_that(mock_popen_constructor.call_count, equal_to(3))

    @patch('subprocess.Popen')
    def test_services_should_not_call_service_action_for_invalid_service_names(self, mock_popen_constructor):
        mock_popen = mock_popen_constructor.return_value = Mock(returncode=0)
        mock_popen.communicate.return_value = ('', '')
        service1, action1 = "service1", "start"
        service2, action2 = "invalid", "start"
        service3, action3 = "service2", "start"
        service4, action4 = "../../tmp/user-program-run-by-root", "start"

        services.services({service1: action1,
                           service2: action2,
                           service3: action3,
                           service4: action4},
                          sentinel.options)

        mock_popen_constructor.assert_any_call(["/etc/init.d/service1", action1], stdout=ANY, stderr=ANY, close_fds=ANY)
        mock_popen_constructor.assert_any_call(["/etc/init.d/service2", action3], stdout=ANY, stderr=ANY, close_fds=ANY)
        assert_that(mock_popen_constructor.call_count, equal_to(2))
