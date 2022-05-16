# Copyright 2010-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import socket


def castint(s):
    if str(s).isdigit():
        return int(s)
    else:
        return s


def splitint(s):
    return list(map(castint, re.findall(r'(\d+|\D+)', str(s))))


def natsort(a, b):
    return cmp(splitint(a), splitint(b))


def is_scalar(var):
    """ Returns True if is scalar or False otherwise """
    return isinstance(var, (str, bool, int, float))


def extract_scalar_from_list(xlist):
    """ Extract scalar values from a list or tuple """
    return [x for x in xlist if is_scalar(x)]


def extract_scalar_from_dict(xdict):
    """ Extract scalar values from a dict natural ordered by key """
    return [xdict[key] for key in sorted(iter(xdict.keys()), natsort)
            if is_scalar(xdict[key])]


def extract_scalar(var):
    """
    Extract scalar from tuple, list and dict
    Return tuple of scalar values
    """
    if isinstance(var, (tuple, list)):
        return tuple(extract_scalar_from_list(var))
    elif isinstance(var, dict):
        return tuple(extract_scalar_from_dict(var))
    elif is_scalar(var):
        return (var,)
    else:
        return


def unique_case_tuple(sequence):
    """ Build an ordered case-insensitive collection """
    xlist = list(dict(list(zip(list(map(str.lower, sequence)), sequence))).values())
    return tuple([x for x in sequence if x in xlist])


# WARNING: the following function does not test the length which must be <= 63
DomainLabelOk = re.compile(r'[a-zA-Z0-9]([-a-zA-Z0-9]*[a-zA-Z0-9])?$').match


def search_domain(search_domain):
    """
    Return True if the search_domain is suitable for use in the search
    line of /etc/resolv.conf, else False.
    """
    # NOTE: 251 comes from FQDN 255 maxi including label length bytes, we
    # do not want to validate search domain beginning or ending with '.',
    # 255 seems to include the final '\0' length byte, so a FQDN is 253
    # char max.  We remove 2 char so that a one letter label requested and
    # prepended to the search domain results in a FQDN that is not too long
    return (
        search_domain
        and len(search_domain) <= 251
        and all(
            (
                ((len(label) <= 63) and DomainLabelOk(label))
                for label in search_domain.split('.')
            )
        )
    )


def is_ipv4_address_valid(addr):
    "True <=> valid"
    try:
        socket.inet_aton(addr)
        return True
    except (TypeError, socket.error):
        return False


def ipv4_address_or_domain(nstr):
    """
    !~ipv4_address_or_domain
        Return True if the document string is an IPv4 address
        or a domain, else False
    """
    return is_ipv4_address_valid(nstr) or search_domain(nstr)


def domain_label(nstr):
    """
    !~domain_label
        Return True if the document string is a domain label, else False
    """
    return DomainLabelOk(nstr) and len(nstr) <= 63
