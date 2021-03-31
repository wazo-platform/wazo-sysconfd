# -*- coding: utf-8 -*-
# Copyright 2013-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import sys

from xivo import http_json_server
from xivo.http_json_server import CMD_R
from xivo.xivo_logging import setup_logging

from wazo_sysconfd.modules import *

from .config import load_config, prepare_http_options


log = logging.getLogger('wazo-sysconfd')


def status_check(args, options):
    return {'status': 'up'}


def main(argv=None):
    "entry point"
    argv = argv or sys.argv[1:]
    http_json_server.register(status_check, CMD_R, name='status-check')

    configuration = load_config(argv)
    setup_logging(configuration['log_file'], log_level=configuration['log_level'])

    http_server_options = prepare_http_options(configuration)
    http_json_server.init(http_server_options)

    try:
        os.umask(022)
        http_json_server.run(http_server_options)
    except SystemExit:
        raise
    except Exception:
        log.exception("bad things happen")


if __name__ == '__main__':
    main()
