#!/usr/bin/env python3

import openstack
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
conn = openstack.connect()

server = conn.compute.find_server(sys.argv[1])

if server:
    metadata = server.get_metadata(conn.compute)
