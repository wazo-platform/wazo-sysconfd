# -*- coding: utf-8 -*-
# Copyright 2013-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os

from xivo import http_json_server
from xivo.http_json_server import CMD_R
from xivo.xivo_logging import setup_logging

from wazo_sysconfd.modules import *

from .config import load_config


log = logging.getLogger('wazo-sysconfd')


def status_check(args, options):
    return {'status': 'up'}


def main():
    "entry point"
    http_json_server.register(status_check, CMD_R, name='status-check')
    options = argv_parse_check()

    configuration = load_config()
    setup_logging(configuration['log_file'], log_level=options.loglevel)

    options.configuration = configuration

    http_json_server.init(options)

    try:
        os.umask(022)
        http_json_server.run(options)
    except SystemExit:
        raise
    except Exception:
        log.exception("bad things happen")


if __name__ == '__main__':
    main()
