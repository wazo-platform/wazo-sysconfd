# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import sys

from xivo.xivo_logging import setup_logging, silence_loggers
from xivo.config_helper import set_xivo_uuid

from .controller import Controller
from .config import load_config

logger = logging.getLogger(__name__)


def main():
    config = load_config(sys.argv[1:])
    setup_logging(
        config['log_file'],
        debug=config['debug'],
        log_level=config['log_level'],
    )
    silence_loggers(('amqp.connection.Connection.heartbeat_tick',), logging.INFO)
    set_xivo_uuid(config, logger)
    controller = Controller(config)
    controller.run()
