#!/bin/bash

while true; do
  ansible-playbook -i inventory/production $0 -vvv;
done
