import subprocess

DHCPD_UDPATE_COMMAND = ['dhcpd-update', '-dr']


def exec_dhcp_update():
    return subprocess.call(DHCPD_UDPATE_COMMAND, close_fds=True)
