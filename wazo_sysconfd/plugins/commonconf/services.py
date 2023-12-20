# Copyright 2010-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import subprocess
import traceback

from wazo_sysconfd import exceptions

logger = logging.getLogger('wazo_sysconfd.modules.commonconf')

commonconf_config = dict()


class CommonConf:
    def safe_init(self, options):
        global commonconf_config
        commonconf_config['file'] = options.get('commonconf', {}).get('commonconf_file')
        commonconf_config['generate_cmd'] = options.get('commonconf', {}).get(
            'commonconf_generate_cmd'
        )
        commonconf_config['update_cmd'] = options.get('commonconf', {}).get(
            'commonconf_update_cmd'
        )
        commonconf_config['monit'] = options.get('commonconf', {}).get(
            'commonconf_monit'
        )
        commonconf_config['monit_checks_dir'] = options.get('monit', {}).get(
            'monit_checks_dir'
        )
        commonconf_config['monit_conf_dir'] = options.get('monit', {}).get(
            'monit_conf_dir'
        )

    def generate_commonconf(self):
        try:
            p = subprocess.Popen(
                [commonconf_config['generate_cmd']],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                close_fds=True,
            )
        except OSError as e:
            logger.exception(e)
            raise exceptions.HttpReqError(500, "can't generate commonconf file")

        ret = p.wait()
        output = p.stdout.read()
        logger.debug("commonconf generate: return code %d" % ret)

        if ret != 0:
            logger.error("Error while generating commonconf: %s", output)
            raise exceptions.HttpReqError(500, "can't generate commonconf file")

    def apply_commonconf(self):
        output = ''
        try:
            p = subprocess.Popen(
                [commonconf_config['update_cmd']],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                close_fds=True,
                encoding='utf-8',
            )
            ret = p.wait()
            output += p.stdout.read()
            logger.debug("commonconf apply: %d" % ret)

            if ret != 0:
                raise exceptions.HttpReqError(500, output)
        except OSError:
            traceback.print_exc()
            raise exceptions.HttpReqError(500, "can't apply commonconf changes")

        try:
            p = subprocess.Popen(
                [commonconf_config['monit']],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                close_fds=True,
                encoding='utf-8',
            )
            ret = p.wait()
            output += '\n' + p.stdout.read()
            logger.debug("monit apply: %d" % ret)

            if ret != 0:
                raise exceptions.HttpReqError(500, output)
        except OSError:
            traceback.print_exc()
            raise exceptions.HttpReqError(500, "can't apply monit changes")

        return output
