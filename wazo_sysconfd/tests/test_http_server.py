# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import unittest

from gunicorn.config import Config
from hamcrest import assert_that, contains_exactly, has_properties
from uvicorn.workers import UvicornWorker

from wazo_sysconfd.http_server import ServiceLogger


class _RecordingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


class TestServiceLogger(unittest.TestCase):
    def setUp(self):
        self.handler = _RecordingHandler()
        root_logger = logging.getLogger()
        self.addCleanup(setattr, root_logger, 'handlers', root_logger.handlers)
        root_logger.handlers = [self.handler]

        self.config = Config()
        self.config.set('loglevel', 'INFO')
        self.config.set('accesslog', '-')
        self.config.set('errorlog', '-')

    def test_gunicorn_logs_at_their_own_level(self):
        logger = ServiceLogger(self.config)

        logger.info('Starting gunicorn')

        assert_that(
            self.handler.records,
            contains_exactly(
                has_properties(
                    name='gunicorn.error',
                    levelno=logging.INFO,
                    msg='Starting gunicorn',
                )
            ),
        )

    def test_uvicorn_logs_through_the_same_handlers(self):
        logger = ServiceLogger(self.config)
        UvicornWorker(0, 0, [], None, 30, self.config, logger)

        logging.getLogger('uvicorn.error').info('Application startup complete.')

        assert_that(
            self.handler.records,
            contains_exactly(
                has_properties(
                    name='uvicorn.error',
                    levelno=logging.INFO,
                    msg='Application startup complete.',
                )
            ),
        )
