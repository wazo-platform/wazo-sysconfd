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

import logging, subprocess

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW
from xivo_sysconf.modules.services import services

logger = logging.getLogger('xivo_sysconf.modules.xivoctl')


def xivoctl(args, options):
    for service, act in args.iteritems():
        if service == 'xivo-service':
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
                logger.exception("Error while executing %s script", service, act)
                raise HttpReqError(500, "can't manage xivoctl")
        else:
            logger.error("service not exist: %s", service)

    return output


http_json_server.register(xivoctl, CMD_RW)
