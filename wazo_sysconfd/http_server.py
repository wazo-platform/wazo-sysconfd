# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from gunicorn.app.base import BaseApplication

from wazo_sysconfd.exceptions import HttpReqError

api = FastAPI(title='wazo-sysconfd', openapi_url='/api/api.yml')


class SysconfdApplication(BaseApplication):
    def __init__(self, *args, config: dict = None, **kwargs):
        self.config = config or {}
        super().__init__(*args, **kwargs)

    def load_config(self):
        host = self.config['rest_api']['listen']
        port = self.config['rest_api']['port']
        self.cfg.set('bind', [f'{host}:{port}'])
        self.cfg.set('default_proc_name', 'sysconfd-api')
        self.cfg.set('loglevel', logging.getLevelName(self.config['log_level']))
        self.cfg.set('accesslog', '-')
        self.cfg.set('errorlog', '-')
        # NOTE: We must set this to one worker, since each worker is its own process, and if we have more than one
        # they will each get their own queue and then not respect the execution order which creates concurrency issues.
        self.cfg.set('workers', 1)
        # NOTE(afournier): that's the magic class that makes gunicorn ASGI
        self.cfg.set('worker_class', 'uvicorn.workers.UvicornWorker')

    def load(self):
        return api


@api.exception_handler(HttpReqError)
async def unicorn_exception_handler(request: Request, exc: HttpReqError):
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message},
    )
