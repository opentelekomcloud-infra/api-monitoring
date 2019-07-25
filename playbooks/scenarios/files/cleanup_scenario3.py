#!/usr/bin/env python3

import openstack
import sys

conn = openstack.connect()

# Script must get 2 prefix for object to cleanup
name_contains = sys.argv[1]

if not name_contains:
    sys.exit(1)

for res in conn.compute.servers():
    if name_contains in res.name:
        conn.compute.delete_server(res.id)
        conn.compute.wait_for_delete(res)

for res in conn.network.security_groups():
    if name_contains in res.name:
        conn.network.delete_security_grouip(res.id)
        conn.network.wait_for_delete(res)

for res in conn.block_storage.volumes():
    if name_contains in res.name:
        conn.block_storage.delete_volume(res.id)
        conn.block_storage.wait_for_delete(res)
