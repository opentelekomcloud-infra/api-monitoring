#!/bin/bash

while true; do
  ansible-playbook -i inventory/testing $1 -vvv;
done
