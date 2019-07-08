#!/usr/bin/env python3

import openstack
import logging
import sys

#openstack.enable_logging(debug=True, http_debug=True)

conn = openstack.connect()
#Until ES150 is completed this query can be done only in old way
#backups = list(conn.block_storage.backups(name=sys.argv[1]))
backups = list(conn.block_storage.backups())
backup = [detail for detail in backups if detail.name == sys.argv[1]]
backup =  next(iter(backup),None)
backup_id = backup.id

backup = conn.block_storage.delete_backup(backup_id)
