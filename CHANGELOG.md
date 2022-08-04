# Changelog

## 22.11

* Code has been rewritten from custom http framework using Python 2 to FastAPI
  using Python 3. There are no changes in the REST API.

## 19.16

* The Asterisk command `sip show peer <peer>` has been removed since it does not work with PJSIP and is not used
* The Asterisk command `core show version` has been removed since it is not used anymore
* The Asterisk command `core show channels` has been removed since it is not used anymore
* The munin module has been removed
* The `/routes` resource has been removed
* The `/swap_ethernet_interfaces` resource has been removed
* The `/rename_ethernet_interfaces` resource has been removed
* The `/network_config` resource has been removed
* The `/netiface_from_dst_address` resource has been removed
* The `/netiface_from_src_address` resource has been removed
* The `/modify_physical_eth_ipv4` resource has been removed
* The `/replace_virtual_eth_ipv4` resource has been removed
* The `/modify_eth_ipv4` resource has been removed
* The `/delete_eth_ipv4` resource has been removed
* the `/change_state_eth_ipv4` resource has been removed
* the `/discover_netifaces` resource has been removed
* the `/netiface` resource has been removed


## 18.14

* The `chown_autoprov_config` request handler has been added
