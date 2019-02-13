# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import subprocess

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW
from xivo_sysconf.modules.services import services

logger = logging.getLogger('xivo_sysconf.modules.xivoctl')


def xivoctl(args, options):
    for service, act in args.iteritems():
        if service == 'wazo-service':
            try:
                if act == 'start':
                    services({'asterisk': 'stop'}, {})
                p = subprocess.Popen(["%s" % service, act],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     close_fds=True)
                output = p.communicate()[0]
                logger.debug("%s %s : %d", service, act, p.returncode)

                if p.returncode != 0:
                    raise HttpReqError(500, output)
            except OSError:
                logger.exception("Error while executing %s script", service)
                raise HttpReqError(500, "can't manage xivoctl")
        else:
            logger.error("service not exist: %s", service)

    return output


http_json_server.register(xivoctl, CMD_RW)
