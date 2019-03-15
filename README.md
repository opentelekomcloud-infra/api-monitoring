# api-monitoring
POC of the platform API monitoring

## Install galaxy roles
```
    ansible-galaxy install -r requirements.yml
```

## Provision
```
    ansible-playbook -i inventory/testing playbooks/main.yaml
```


## results

os_server_present ----------------------------------------------- 143.60s
os_floating_ip_present ------------------------------------------ 12.02s
os_server_facts_unchanged --------------------------------------- 9.51s
os_router_present ----------------------------------------------- 6.31s
os_security_group_rule_present ---------------------------------- 3.03s
os_subnet_present ----------------------------------------------- 2.84s
os_keypair_present ---------------------------------------------- 2.65s
os_server_facts_unchanged --------------------------------------- 2.54s
os_security_group_rule_present ---------------------------------- 2.50s
os_network_present ---------------------------------------------- 2.31s
os_security_group_present --------------------------------------- 1.96s
