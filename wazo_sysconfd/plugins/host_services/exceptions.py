# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class InvalidActionException(ValueError):
    def __init__(self, service_name, action):
        super().__init__()
        self.service_name = service_name
        self.action = action


class InvalidServiceException(ValueError):
    def __init__(self, service_name):
        super().__init__()
        self.service_name = service_name
