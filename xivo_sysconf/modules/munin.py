# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
import subprocess

from xivo import http_json_server
from xivo.http_json_server import CMD_R


class Munin(object):

    def __init__(self):
        super(Munin, self).__init__()
        self.log = logging.getLogger('xivo_sysconf.modules.munin')

        http_json_server.register(self.update, CMD_R,
                                  safe_init=self.safe_init,
                                  name='munin_update')

        self.cmd1 = ['/usr/sbin/xivo-monitoring-update']
        self.cmd2 = ['/usr/bin/munin-cron', '--force-root']

    def safe_init(self, options):
        pass

    def update(self, args, options):
        try:
            p = subprocess.Popen(self.cmd1, close_fds=True)
            ret = p.wait()
        except Exception:
            self.log.debug("can't execute '%s'" % self.cmd1)
            raise http_json_server.HttpReqError(500, "can't execute '%s'" % self.cmd1)
        if ret != 0:
            raise http_json_server.HttpReqError(500, "'%s' process return error %d" % (self.cmd1, ret))

        try:
            p = subprocess.Popen(self.cmd2, close_fds=True)
        except Exception:
            self.log.debug("can't execute '%s'" % self.cmd2)
            raise http_json_server.HttpReqError(500, "can't execute '%s'" % self.cmd2[0])

        return True


munin = Munin()
