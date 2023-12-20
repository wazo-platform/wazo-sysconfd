# Copyright 2010-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
from shutil import copy2
from time import time

from xivo import system

from wazo_sysconfd import helpers
from wazo_sysconfd.dns_lock import RESOLVCONFLOCK
from wazo_sysconfd.exceptions import HttpReqError
from wazo_sysconfd.utilities import txtsubst

log = logging.getLogger('wazo_sysconfd.plugins.resolvconf')

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

    if not os.path.isdir(Rcc[f"{optname}_backup_path"]):
        os.makedirs(Rcc[f"{optname}_backup_path"])

    if os.access(Rcc[f"{optname}_file"], os.R_OK):
        backupfilename = f"{Rcc[f'{optname}_backup_file']}.{int(time())}"
        copy2(Rcc[f"{optname}_file"], backupfilename)

    if os.access(Rcc[f"{optname}_custom_tpl_file"], (os.F_OK | os.R_OK)):
        filename = Rcc[f"{optname}_custom_tpl_file"]
    else:
        filename = Rcc[f"{optname}_tpl_file"]

    template_file = open(filename)
    template_lines = template_file.readlines()
    template_file.close()

    txt = txtsubst(
        template_lines,
        xvars,
        Rcc[f"{optname}_file"],
        'utf8',
    )

    system.file_writelines_flush_sync(Rcc[f"{optname}_file"], txt)

    return backupfilename


def _validate_hosts(args):
    if not helpers.domain_label(args.get('hostname')):
        raise HttpReqError(415, "invalid arguments for command")
    if not helpers.search_domain(args.get('domain')):
        raise HttpReqError(415, "invalid arguments for command")


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
    xvars = {
        '_XIVO_NAMESERVER_LIST': os.linesep.join(
            f'nameserver {nameserver}' for nameserver in args['nameservers']
        )
    }

    if 'search' in args:
        xvars['_XIVO_DNS_SEARCH'] = f"search {' '.join(args['search'])}"
    else:
        xvars['_XIVO_DNS_SEARCH'] = ""

    return xvars


def resolv_conf(args, options):
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
            raise HttpReqError(
                415, f"duplicated nameservers in {list(args['nameservers'])!r}"
            )

    if 'search' in args:
        args['search'] = helpers.extract_scalar(args['search'])
        search = helpers.unique_case_tuple(args['search'])

        if len(search) == len(args['search']):
            args['search'] = list(search)
        else:
            raise HttpReqError(415, f"duplicated search in {list(args['search'])!r}")

        if len(''.join(args['search'])) > 255:
            raise HttpReqError(
                415,
                f"maximum length exceeded for option search: {list(args['search'])!r}",
            )

    _validate_resolv_conf(args)

    if not os.access(Rcc['resolvconf_path'], (os.X_OK | os.W_OK)):
        raise HttpReqError(
            415,
            f"path not found or not writable or not executable: {Rcc['resolvconf_path']!r}",
        )

    if not RESOLVCONFLOCK.acquire_read(Rcc['lock_timeout']):
        raise HttpReqError(
            503,
            f"unable to take RESOLVCONFLOCK for reading after {Rcc['lock_timeout']} seconds",
        )

    resolvconfbakfile = None

    try:
        try:
            resolvconfbakfile = _write_config_file(
                'resolvconf', _resolv_conf_variables(args)
            )
            return True
        except Exception as e:
            if resolvconfbakfile:
                copy2(resolvconfbakfile, Rcc['resolvconf_file'])
            raise e.__class__(str(e))
    finally:
        RESOLVCONFLOCK.release()


def safe_init(options):
    """Load parameters, etc"""
    global Rcc

    tpl_path = options.get('templates_path')
    custom_tpl_path = options.get('custom_templates_path')
    backup_path = options.get('backup_path')

    if options.get('resolvconf'):
        for x in Rcc.keys():
            if options['resolvconf'].get(x):
                Rcc[x] = options['resolvconf'].get(x)

    Rcc['lock_timeout'] = float(Rcc['lock_timeout'])

    for optname in ('hostname', 'hosts', 'resolvconf'):
        Rcc[f"{optname}_tpl_file"] = os.path.join(tpl_path, Rcc[f"{optname}_tpl_file"])

        Rcc[f"{optname}_custom_tpl_file"] = os.path.join(
            custom_tpl_path,
            Rcc[f"{optname}_tpl_file"],
        )

        Rcc[f"{optname}_path"] = os.path.dirname(Rcc[f"{optname}_file"])
        Rcc[f"{optname}_backup_file"] = os.path.join(
            backup_path,
            Rcc[f"{optname}_file"].lstrip(os.path.sep),
        )
        Rcc[f"{optname}_backup_path"] = os.path.join(
            backup_path,
            Rcc[f"{optname}_path"].lstrip(os.path.sep),
        )
