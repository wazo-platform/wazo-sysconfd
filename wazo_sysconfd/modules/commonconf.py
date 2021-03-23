# -*- coding: utf-8 -*-
# Copyright 2010-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import subprocess
import traceback
from xivo import http_json_server
from xivo.http_json_server import CMD_RW, CMD_R, HttpReqError

logger = logging.getLogger('wazo_sysconfd.modules.commonconf')


class CommonConf(object):

    def __init__(self):
        http_json_server.register(self.generate, CMD_RW,
                                  safe_init=self.safe_init,
                                  name='commonconf_generate')
        http_json_server.register(self.apply, CMD_R, name='commonconf_apply')

    def safe_init(self, options):
        self.file = options.configuration.get('commonconf', {}).get('commonconf_file')
        self.generate_cmd = options.configuration.get('commonconf', {}).get('commonconf_generate_cmd')
        self.update_cmd = options.configuration.get('commonconf', {}).get('commonconf_update_cmd')
        self.monit = options.configuration.get('commonconf', {}).get('commonconf_monit')
        self.monit_checks_dir = options.configuration.get('monit', {}).get('monit_checks_dir')
        self.monit_conf_dir = options.configuration.get('monit', {}).get('monit_conf_dir')

    def generate(self, args, options):
        try:
            p = subprocess.Popen([self.generate_cmd],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)
        except OSError as e:
            logger.exception(e)
            raise HttpReqError(500, "can't generate commonconf file")

        ret = p.wait()
        output = p.stdout.read()
        logger.debug("commonconf generate: return code %d" % ret)

        if ret != 0:
            logger.error("Error while generating commonconf: %s", output)
            raise HttpReqError(500, "can't generate commonconf file")

    def apply(self, args, options):
        output = ''
        try:
            p = subprocess.Popen([self.update_cmd],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)
            ret = p.wait()
            output += p.stdout.read()
            logger.debug("commonconf apply: %d" % ret)

            if ret != 0:
                raise HttpReqError(500, output)
        except OSError:
            traceback.print_exc()
            raise HttpReqError(500, "can't apply commonconf changes")

        try:
            p = subprocess.Popen([self.monit],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)
            ret = p.wait()
            output += '\n' + p.stdout.read()
            logger.debug("monit apply: %d" % ret)

            if ret != 0:
                raise HttpReqError(500, output)
        except OSError:
            traceback.print_exc()
            raise HttpReqError(500, "can't apply monit changes")

        return output


commonconf = CommonConf()
