#!/usr/bin/env python3

import openstack
import sys


conn = openstack.connect()

backup_found = False
for backup in conn.block_storage.backups():
    if backup.name == sys.argv[1]:
        if backup_found:
            print('Backup with this name was already found, potentially'
                  'multiple')
        backup_found = True
        conn.block_storage.delete_backup(backup.id)
        conn.block_storage.wait_for_delete(backup, interval=2, wait=300)
