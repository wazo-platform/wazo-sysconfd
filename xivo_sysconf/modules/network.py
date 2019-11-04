# -*- coding: utf-8 -*-
# Copyright 2008-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_R
from xivo.moresynchro import RWLock
from xivo import xivo_config
from xivo import yaml_json


NET_LOCK_TIMEOUT = 60  # XXX
NETLOCK = RWLock()


def network_config(args):
    """
    GET /network_config

    Just returns the network configuration
    """
    if not NETLOCK.acquire_read(NET_LOCK_TIMEOUT):
        raise HttpReqError(503, "unable to take NETLOCK for reading after %s seconds" % NET_LOCK_TIMEOUT)
    try:
        netconf = xivo_config.load_current_configuration()
        return yaml_json.stringify_keys(netconf)
    finally:
        NETLOCK.release()


http_json_server.register(network_config, CMD_R)
