#!/usr/bin/env python3

import openstack
import logging
import sys

#openstack.enable_logging(debug=True, http_debug=True)

conn = openstack.connect()
#Until ES150 is completed this query can be done only in old way
#backups = list(conn.block_storage.backups(name=sys.argv[1]))
backups = list(conn.block_storage.backups())
backup_found = False
for backup in conn.block_storage.backups():
    if backup.name == sys.argv[1]:
        if backup_found:
            print('Backup with this name was already found, potentially'
                  'multiple')
        backup_found = True
        conn.block_storage.delete_backup(backup.id)
