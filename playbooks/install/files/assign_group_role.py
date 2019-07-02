#!/usr/bin/env python3

import argparse
import logging
import openstack


def assign_roles_to_group(conn, group, project, roles, fake=False):
    group = conn.identity.find_group(group).id
    project = conn.identity.find_project(project).id
    if not fake:
        for role in roles:
            role_obj = conn.identity.find_role(role)
            conn.identity.assign_project_role_to_group(
                project=project,
                group=group,
                role=role_obj.id
            )
    else:
        logging.debug('Not assigning roles to group')

def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('project')
    parser.add_argument('group')
    args = parser.parse_args()
    conn = openstack.connect()
    roles = [
        'server_adm',
        'te_admin'
    ]
    assign_roles_to_group(conn, args.group, args.project, roles)

if __name__== "__main__":
  main()
