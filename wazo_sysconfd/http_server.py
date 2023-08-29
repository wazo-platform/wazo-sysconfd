# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from gunicorn.app.base import BaseApplication

from wazo_sysconfd.bus import BusManager
from wazo_sysconfd.exceptions import HttpReqError

api = FastAPI(title='wazo-sysconfd', openapi_url='/api/api.yml')


class SysconfdApplication(BaseApplication):
    def __init__(self, *args, config: dict = None, bus_manager: BusManager, **kwargs):
        self.config = config or {}
        self.bus_manager = bus_manager
        super().__init__(*args, **kwargs)

    def load_config(self):
        host = self.config['rest_api']['listen']
        port = self.config['rest_api']['port']
        self.cfg.set('bind', [f'{host}:{port}'])
        self.cfg.set('default_proc_name', 'sysconfd-api')
        self.cfg.set('loglevel', logging.getLevelName(self.config['log_level']))
        self.cfg.set('accesslog', '-')
        self.cfg.set('errorlog', '-')
        self.cfg.set('post_worker_init', self.post_worker_init)
        self.cfg.set('on_exit', self.on_exit)
        # NOTE: We must set this to one worker, since each worker is its own process, and if we have more than one
        # they will each get their own queue and then not respect the execution order which creates concurrency issues.
        self.cfg.set('workers', 1)
        # NOTE(afournier): that's the magic class that makes gunicorn ASGI
        self.cfg.set('worker_class', 'uvicorn.workers.UvicornWorker')

    def load(self):
        return api

    # Because gunicorn is using the forking model, We must deactivate the multiprocessing atexit default handler.
    # If not, it will trigger an exception when shutting down (thinking it owns the bus_manager process)
    def post_worker_init(self, worker):
        import atexit
        from multiprocessing.util import _exit_function

        atexit.unregister(_exit_function)

    def on_exit(self, server):
        self.bus_manager.stop()


@api.exception_handler(HttpReqError)
async def unicorn_exception_handler(request: Request, exc: HttpReqError):
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message},
    )
