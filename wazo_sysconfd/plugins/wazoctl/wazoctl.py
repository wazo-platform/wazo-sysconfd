# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import subprocess

from wazo_sysconfd.exceptions import HttpReqError
from wazo_sysconfd.plugins.services.services import services

logger = logging.getLogger('wazo_sysconfd.modules.wazoctl')


def wazoctl(args, options):
    for service, act in args.items():
        if service == 'wazo-service':
            try:
                if act == 'start':
                    services({'asterisk': 'stop'})
                p = subprocess.Popen(
                    [f"{service}", act],
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
                raise HttpReqError(500, "can't manage wazoctl")
        else:
            logger.error("service not exist: %s", service)

    return output
