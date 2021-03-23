# -*- coding: utf-8 -*-
# Copyright 2010-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import logging
import subprocess

from time import time
from shutil import copy2

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW
from xivo.moresynchro import RWLock
from xivo.xivo_config import txtsubst
from xivo import system

from wazo_sysconfd import helpers

log = logging.getLogger('wazo_sysconfd.modules.resolvconf')

RESOLVCONFLOCK = RWLock()

Rcc = {
    'hostname_file': os.path.join(os.path.sep, 'etc', 'hostname'),
    'hostname_tpl_file': os.path.join('resolvconf', 'hostname'),
    'hosts_file': os.path.join(os.path.sep, 'etc', 'hosts'),
    'hosts_tpl_file': os.path.join('resolvconf', 'hosts'),
    'resolvconf_file': os.path.join(os.path.sep, 'etc', 'resolv.conf'),
    'resolvconf_tpl_file': os.path.join('resolvconf', 'resolv.conf'),
    'lock_timeout': 60,
}


def _write_config_file(optname, xvars):
    backupfilename = None

    if not os.path.isdir(Rcc["%s_backup_path" % optname]):
        os.makedirs(Rcc["%s_backup_path" % optname])

    if os.access(Rcc["%s_file" % optname], os.R_OK):
        backupfilename = "%s.%d" % (Rcc["%s_backup_file" % optname], time())
        copy2(Rcc["%s_file" % optname], backupfilename)

    if os.access(Rcc["%s_custom_tpl_file" % optname], (os.F_OK | os.R_OK)):
        filename = Rcc["%s_custom_tpl_file" % optname]
    else:
        filename = Rcc["%s_tpl_file" % optname]

    template_file = open(filename)
    template_lines = template_file.readlines()
    template_file.close()

    txt = txtsubst(
        template_lines,
        xvars,
        Rcc["%s_file" % optname],
        'utf8',
    )

    system.file_writelines_flush_sync(Rcc["%s_file" % optname], txt)

    return backupfilename


def _validate_hosts(args):
    if not helpers.domain_label(args.get('hostname')):
        raise HttpReqError(415, "invalid arguments for command")
    if not helpers.search_domain(args.get('domain')):
        raise HttpReqError(415, "invalid arguments for command")


def Hosts(args, options):
    """
    POST /hosts

    >>> hosts({'hostname':  'xivo',
               'domain':    'localdomain'})
    """
    _validate_hosts(args)

    if not os.access(Rcc['hostname_path'], (os.X_OK | os.W_OK)):
        raise HttpReqError(
            415,
            "path not found or not writable or not executable: %r" % Rcc['hostname_path'],
        )

    if not os.access(Rcc['hosts_path'], (os.X_OK | os.W_OK)):
        raise HttpReqError(
            415,
            "path not found or not writable or not executable: %r" % Rcc['hosts_path'],
        )

    if not RESOLVCONFLOCK.acquire_read(Rcc['lock_timeout']):
        raise HttpReqError(
            503,
            "unable to take RESOLVCONFLOCK for reading after %s seconds" % Rcc['lock_timeout'],
        )

    hostnamebakfile = None
    hostsbakfile = None

    try:
        try:
            hostnamebakfile = _write_config_file(
                'hostname', {'_XIVO_HOSTNAME': args['hostname']},
            )

            hostsbakfile = _write_config_file(
                'hosts', {'_XIVO_HOSTNAME': args['hostname'], '_XIVO_DOMAIN': args['domain']},
            )

            subprocess.call(['hostname', '-F', Rcc['hostname_file']])

            return True
        except Exception, e:
            if hostnamebakfile:
                copy2(hostnamebakfile, Rcc['hostname_file'])
            if hostsbakfile:
                copy2(hostsbakfile, Rcc['hosts_file'])
            raise e.__class__(str(e))
    finally:
        RESOLVCONFLOCK.release()


def _validate_resolv_conf(args):
    nameservers = args.get('nameservers', [])
    if not 0 < len(nameservers) < 4:
        raise HttpReqError(415, "invalid arguments for command")
    for nameserver in nameservers:
        if not helpers.ipv4_address_or_domain(nameserver):
            raise HttpReqError(415, "invalid arguments for command")

    searches = args.get('search', [])
    if not 0 < len(searches) < 7:
        raise HttpReqError(415, "invalid arguments for command")
    for search in searches:
        if not helpers.search_domain(search):
            raise HttpReqError(415, "invalid arguments for command")


def _resolv_conf_variables(args):
    xvars = {}
    xvars['_XIVO_NAMESERVER_LIST'] = \
        os.linesep.join(["nameserver %s"] * len(args['nameservers'])) % tuple(args['nameservers'])

    if 'search' in args:
        xvars['_XIVO_DNS_SEARCH'] = "search %s" % " ".join(args['search'])
    else:
        xvars['_XIVO_DNS_SEARCH'] = ""

    return xvars


def ResolvConf(args, options):
    """
    POST /resolv_conf

    >>> resolv_conf({'nameservers': '192.168.0.254'})
    >>> resolv_conf({'nameservers': ['192.168.0.254', '10.0.0.254']})
    >>> resolv_conf({'search': ['toto.tld', 'tutu.tld']
                     'nameservers': ['192.168.0.254', '10.0.0.254']})
    """

    if 'nameservers' in args:
        args['nameservers'] = helpers.extract_scalar(args['nameservers'])
        nameservers = helpers.unique_case_tuple(args['nameservers'])

        if len(nameservers) == len(args['nameservers']):
            args['nameservers'] = list(nameservers)
        else:
            raise HttpReqError(415, "duplicated nameservers in %r" % list(args['nameservers']))

    if 'search' in args:
        args['search'] = helpers.extract_scalar(args['search'])
        search = helpers.unique_case_tuple(args['search'])

        if len(search) == len(args['search']):
            args['search'] = list(search)
        else:
            raise HttpReqError(415, "duplicated search in %r" % list(args['search']))

        if len(''.join(args['search'])) > 255:
            raise HttpReqError(
                415,
                "maximum length exceeded for option search: %r" % list(args['search']),
            )

    _validate_resolv_conf(args)

    if not os.access(Rcc['resolvconf_path'], (os.X_OK | os.W_OK)):
        raise HttpReqError(
            415,
            "path not found or not writable or not executable: %r" % Rcc['resolvconf_path'],
        )

    if not RESOLVCONFLOCK.acquire_read(Rcc['lock_timeout']):
        raise HttpReqError(
            503,
            "unable to take RESOLVCONFLOCK for reading after %s seconds" % Rcc['lock_timeout'],
        )

    resolvconfbakfile = None

    try:
        try:
            resolvconfbakfile = _write_config_file('resolvconf', _resolv_conf_variables(args))
            return True
        except Exception, e:
            if resolvconfbakfile:
                copy2(resolvconfbakfile, Rcc['resolvconf_file'])
            raise e.__class__(str(e))
    finally:
        RESOLVCONFLOCK.release()


def safe_init(options):
    """Load parameters, etc"""
    global Rcc

    cfg = options.configuration

    tpl_path = cfg.get('templates_path')
    custom_tpl_path = cfg.get('custom_templates_path')
    backup_path = cfg.get('backup_path')

    if cfg.get('resolvconf'):
        for x in Rcc.iterkeys():
            if cfg['resolvconf'].get(x):
                Rcc[x] = cfg['resolvconf'].get(x)

    Rcc['lock_timeout'] = float(Rcc['lock_timeout'])

    for optname in ('hostname', 'hosts', 'resolvconf'):
        Rcc["%s_tpl_file" % optname] = os.path.join(tpl_path, Rcc["%s_tpl_file" % optname])

        Rcc["%s_custom_tpl_file" % optname] = os.path.join(
            custom_tpl_path, Rcc["%s_tpl_file" % optname],
        )

        Rcc["%s_path" % optname] = os.path.dirname(Rcc["%s_file" % optname])
        Rcc["%s_backup_file" % optname] = os.path.join(
            backup_path, Rcc["%s_file" % optname].lstrip(os.path.sep),
        )
        Rcc["%s_backup_path" % optname] = os.path.join(
            backup_path, Rcc["%s_path" % optname].lstrip(os.path.sep),
        )


http_json_server.register(Hosts, CMD_RW, safe_init=safe_init, name='hosts')
http_json_server.register(ResolvConf, CMD_RW, name='resolv_conf')
