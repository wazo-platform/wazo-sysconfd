# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import subprocess

from wazo_sysconfd.exceptions import HttpReqError
from wazo_sysconfd.plugins.host_services.services import services

logger = logging.getLogger('wazo_sysconfd.modules.xivoctl')


def xivoctl(args, options):
    for service, act in args.items():
        if service == 'wazo-service':
            try:
                if act == 'start':
                    services({'asterisk': 'stop'})
                p = subprocess.Popen(
                    ["%s" % service, act],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                )
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
