# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import FastAPI
from gunicorn.app.base import BaseApplication

api = FastAPI(title='wazo-sysconfd', openapi_url='/api/api.yml')


def ensure_list(obj):
    if not isinstance(obj, list):
        return [obj]
    else:
        return obj


class SysconfdApplication(BaseApplication):
    def __init__(self, *args, config: dict = None, **kwargs):
        self.config = config or {}
        super().__init__(*args, **kwargs)

    def load_config(self):
        host = self.config['rest_api']['listen']
        port = self.config['rest_api']['port']
        self.cfg.set('bind', [f'{host}:{port}'])
        self.cfg.set('default_proc_name', 'sysconfd-api')
        self.cfg.set('loglevel', self.config['log_level'])
        self.cfg.set('accesslog', '-')
        self.cfg.set('errorlog', '-')
        self.cfg.set('workers', self.config['workers'])
        # NOTE(afournier): that's the magic class that makes gunicorn ASGI
        self.cfg.set('worker_class', 'uvicorn.workers.UvicornWorker')

    def load(self):
        return api
