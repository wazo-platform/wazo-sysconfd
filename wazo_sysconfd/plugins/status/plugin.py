# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import Depends

from .http import router


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']
        status_aggregator = dependencies['status_aggregator']

        # NOTE(afournier): FastAPI requires callables for dependencies
        api.include_router(router, dependencies=[Depends(lambda: status_aggregator)])
