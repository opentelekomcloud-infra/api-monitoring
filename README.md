# api-monitoring
POC of the platform API monitoring

A High-level design of the APImon system is available under [HLD](docs/design.rst)

THIS IS A VERY VERY DRAFT

## Install galaxy roles

Multiple playbooks are using galaxy roles, so it is required to install those.

```
    ansible-galaxy install -r requirements.yml
```

## Installation

The APIMon can be deployed in multiple environments to keep testing from different places (please see [HLD]/docs/design.rst). There is currently a set of playbook, which helps installing APImon on to the OpenStack based platform (what is actually naturally the scope of the project). If hardware (or VMs for components already exist, or not supported by the infrastructure installation playbooks), infrastructure preparation can be skipped.

The APIMon consists of 4 components:
 - bastion - bastion host for the infrastructure with floating IP
 - executor - host running jobs and telegraf (for metrics forwarding)
 - influxdb - an InfluxDB instance as a TimeSeries DB
 - grafana - instance of Grafana, which shows gathered metrics

### Prerequisites
	
 - ansible - should be at least 2.8.1
 - python3-openstacksdk - should be at least 0.26.x

### Inventory

Inventory must be prepared, already before the infrastructure can be provisioned. This is required to know how to name resources, which FQDNs to use, which private keys to use to access instances.

Inventory consists of following components:

- hosts.yaml - contains host-relevant data (ips, access data, host-specific passwords, etc)
- group_vars/all.yaml - contains common variables, ssl keys, domain name, etc
- group_vars/os_infra.yaml - data relevant for the infrastructure provisioning (keys, security groups, flavors, etc.)
- group_vars/grafana.yaml - variables for the grafana target
- group_vars/influxdb.yaml - variables for influxdb
- group_vars/executor.yaml - executor variables
- group_vars/telegraf.yaml - telegraf variables

### Infrastructure provisioning

Ansible can be used to provision infrastructure on top of the OpenStack, For that a proper cloud connection should be present on the management host (presumably localhost) - clouds.yaml


```
    ansible-playbook -i inventory/production playbooks/install/provision_infra.yaml
```

This step creates 4 instances (bastion, executor+telegraf, influx, grafana), load balancer.

The next step will be to configure connections and inventory with the newly created instances. This consists of few steps:

1. Configuring bastion host in the ~/.ssh/config to be proxying connections
```
   Host apimon-bastion
   HostName 80.158.7.107
   User linux
   ControlMaster auto
   ControlPersist 5m
```

2. Modify inventory/production/hosts.yaml with IP addresses of the instances. It is also a time to fill the inventory with the proper initial secrets (i.e. for influxdb admin user). One option would be to execute `< /dev/urandom tr -fc _A-Z-a-z-0-9 | head -c${1:-32};echo;`


### Installation

When target hosts are present, configured in the inventory the required software can be provisioned there:

```
  ansible -i inventory/production playbooks/install/bootstrap.yaml
```


Playbooks description:
 - install/bootstrap.yaml - provisions `server_common` role to all inventory hosts (especially to be able to access hosts behind bastion, mount attached volumes to required places and installs influxdb and grafana.
 - install/install_influxdb.yaml - included in the bootstrap.yaml. Indivudial steps for influxdb provisioning (installation, creation of admin user and apimon database). Users for telegraf and grafana are not created in this step.
 - install/install_grafana.yaml - included in the bootstrap.yaml. Individual steps for grafans provisioning (installation). Provisioning stuff is mounted into the container running grafana, but it is intended, that datasources are installed separately by "connection" another instance of influxdb into the map.
 - install/install_executor.yaml - included in the bootstrap.yaml. Individual steps for executor host provisioning. It includes local telegraf container (forwards influxdb writes to real InfluxDB) and the executor itself.
 - install/connect_influx_to_grafana.yaml - Creates a read-only user for grafana on a specific (user-input) influxdb instance and provision corresponding datasource to the grafana. A random password is generated for that and not really saved anywhere (except datasource itself).

After bootstrap step it is required to connect influxdb and grafana by executing `playbooks/install/connect_influx_to_grafana.yaml` playbook. After that step a proper datasource is available in grafana. Dashboards/pannels are not installed automatically as of now.

In addition current state is that building image on the executor hangs (propably TCPForward connection issue) and Ansible does not recognize, when the process is stopped. So it is required to abort at this step after around 5 minutes (yes, will be fixed ASAP). After that you can manually execute `sudo systemctl start executor-service` on the executor host. As already mentioned dashboard is not provisioned currently, so no data will be visible in grafana.


### Test project creation

There is a playbook for creating a standalone project/user_group/user where the tests might be executed. 

```
  OS_CLOUD=cloud_with_domain_scope -i inventory/production playbooks/install/create_test_project.yaml
```

This playbook takes `test_project_name`, `test_domain_name`, `test_user_name`, `test_user_password` and creates corresponding project, user_group and user correspondigly. Currently the script contains predefined list of roles to be assigned to the group, so if those are different in the target environment (which most likely is) - adapt script.


## Developer setup

#NOTE:# This is under reworking currently to reuse as much pieces from the proper installation as possible.

It is possible to use tools for development purposes locally with the help of docker-compose (P.S. minishift/minikube would be nice to have)
In order to start it prepare inventory by copying testing inventory folder into something useful (please note testing inventory is saved in git, therefore please do not place any sensitive information. Inventory/production is excluded by gitignore not to accidentially leak data) and modify data as you need (especially cloud credentials in the clouds.yaml must be real).
After this step is done you can start stack by running:
```
    docker-compose up
```

This will build and start 4 containers. Executor will start executing test scenarios and populate InfluxDB. Grafana instance is listening on the localhost port 3000 and can be used to visualize data (default access credentials: 'admin:foobar').
