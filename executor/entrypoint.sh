#!/bin/bash

cd /usr/app

git clone https://github.com/opentelekomcloud-infra/api-monitoring

cd api-monitoring

# while true; do
#
#   echo "Generating new values";
#   for metric in 'identity.GET.token' 'compute.POST.server' 'compute.DELETE.server' 'image.PUT.image'; do
#     val="${RANDOM}.000000";
#     echo "openstack.api.$metric:${RANDOM}|ms" | nc -w1 -u telegraf 8125;
#   done;
#   sleep 1;
#   python3 test.py
# done;

for playbook in playbooks/*; do
  ./executor/scripts/execute_playbook.sh "${playbook}" &
done
wait
