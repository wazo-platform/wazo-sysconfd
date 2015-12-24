# -*- coding: utf-8 -*-

# Copyright (C) 2010-2015 Avencall
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

import logging
import subprocess

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW

logger = logging.getLogger('xivo_sysconf.modules.services')


class InvalidActionException(ValueError):
    def __init__(self, service_name, action):
        super(InvalidActionException, self).__init__(self)
        self.service_name = service_name
        self.action = action


class InvalidServiceException(ValueError):
    def __init__(self, service_name):
        super(InvalidServiceException, self).__init__(self)
        self.service_name = service_name


def services(args, options):
    """
    POST /services

    >>> services({'networking': 'restart'})
    """
    output = ''
    for service, action in args.iteritems():
        output += _run_action_for_service(service, action)

    return output


def _run_action_for_service(service, action):
    output = ''
    try:
        _validate_action(service, action)
        output = _run_action_for_service_validated(service, action)
    except InvalidActionException as e:
        logger.error("action %s not authorized on %s service", e.action, e.service_name)
    except InvalidServiceException as e:
        logger.error("service %s is not valid", e.service_name)
    return output


def _validate_action(service_name, action):
    if action not in ['stop', 'start', 'restart']:
        raise InvalidActionException(service_name, action)


def _run_action_for_service_validated(service, action):
    output = ''
    try:
        command = ['/bin/systemctl', action, '{}.service'.format(service)]
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=True)
        output = p.communicate()[0]
        logger.debug("%s : return code %d", ' '.join(command), p.returncode)

        if p.returncode != 0:
            raise HttpReqError(500, output)
    except OSError:
        logger.exception("Error while executing action")
        raise HttpReqError(500, "can't manage services")

    return output


http_json_server.register(services, CMD_RW, name='services')
