# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from xivo.xivo_logging import setup_logging

from .controller import Controller
from .config import load_config


def main():
    config = load_config(sys.argv[1:])
    setup_logging(config['log_file'], log_level=config['log_level'])
    controller = Controller(config)
    controller.run()
