# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase
from unittest.mock import ANY, Mock, patch

from hamcrest import assert_that, equal_to

from .. import services


class TestServices(TestCase):
    def setUp(self):
        services_on_disk = ['service%s' % i for i in range(1, 10)]
        self.patcher = patch('os.listdir', return_value=services_on_disk)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_services_should_return_empty_string_when_called_with_empty_dict(self):
        result = services.services({})

        assert_that(result, equal_to(''))

    @patch('subprocess.Popen')
    def test_services_should_call_service_action_for_each_service(
        self, mock_popen_constructor
    ):
        mock_popen = mock_popen_constructor.return_value = Mock(returncode=0)
        mock_popen.communicate.return_value = ('', '')
        service1, action1 = "service1", "start"
        service2, action2 = "service2", "stop"

        services.services({service1: action1, service2: action2})

        mock_popen_constructor.assert_any_call(
            ["/bin/systemctl", action1, "service1.service"],
            stdout=ANY,
            stderr=ANY,
            close_fds=ANY,
            encoding="UTF-8",
        )
        mock_popen_constructor.assert_any_call(
            ["/bin/systemctl", action2, "service2.service"],
            stdout=ANY,
            stderr=ANY,
            close_fds=ANY,
            encoding="UTF-8",
        )

    @patch('subprocess.Popen')
    def test_services_should_not_call_service_action_for_invalid_actions_service(
        self, mock_popen_constructor
    ):
        mock_popen = mock_popen_constructor.return_value = Mock(returncode=0)
        mock_popen.communicate.return_value = ('', '')
        service1, action1 = "service1", "start"
        service2, action2 = "service2", "invalid"
        service3, action3 = "service3", "restart"
        service4, action4 = "service4", "invalid2"
        service5, action5 = "service5", "stop"

        services.services(
            {
                service1: action1,
                service2: action2,
                service3: action3,
                service4: action4,
                service5: action5,
            }
        )

        mock_popen_constructor.assert_any_call(
            ["/bin/systemctl", action1, "service1.service"],
            stdout=ANY,
            stderr=ANY,
            close_fds=ANY,
            encoding="UTF-8",
        )
        mock_popen_constructor.assert_any_call(
            ["/bin/systemctl", action3, "service3.service"],
            stdout=ANY,
            stderr=ANY,
            close_fds=ANY,
            encoding="UTF-8",
        )
        mock_popen_constructor.assert_any_call(
            ["/bin/systemctl", action5, "service5.service"],
            stdout=ANY,
            stderr=ANY,
            close_fds=ANY,
            encoding="UTF-8",
        )
        assert_that(mock_popen_constructor.call_count, equal_to(3))
