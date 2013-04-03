# -*- coding: utf-8 -*-

# Copyright (C) 2010-2013 Avencall
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

__author__  = "Guillaume Bour <gbour@proformatique.com>"

import logging, subprocess

from xivo import http_json_server
from xivo.http_json_server import CMD_R


class Munin(object):
    def __init__(self):
        super(Munin, self).__init__()
        self.log = logging.getLogger('xivo_sysconf.modules.munin')

        http_json_server.register(self.update , CMD_R,
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
