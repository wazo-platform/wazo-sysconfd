# Copyright 2010-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import subprocess

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW
from . import exceptions

logger = logging.getLogger('wazo_sysconfd.modules.services')


def services(args):
    """
    POST /services

    >>> services({'networking': 'restart'})
    """
    output = ''
    for service, action in args.items():
        output += _run_action_for_service(service, action)

    return output


def _run_action_for_service(service, action):
    output = ''
    try:
        _validate_action(service, action)
        output = _run_action_for_service_validated(service, action)
    except exceptions.InvalidActionException as e:
        logger.error("action %s not authorized on %s service", e.action, e.service_name)
    except exceptions.InvalidServiceException as e:
        logger.error("service %s is not valid", e.service_name)
    return output


def _validate_action(service_name, action):
    if action not in ['stop', 'start', 'restart']:
        raise exceptions.InvalidActionException(service_name, action)


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

    if isinstance(output, bytes):
        return output.decode("utf-8")
    else:
        return output 


http_json_server.register(services, CMD_RW, name='services')