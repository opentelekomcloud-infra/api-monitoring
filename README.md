# api-monitoring
POC of the platform API monitoring

A High-level design of the APImon system is available under [HLD](docs/design.rst)

THIS IS A VERY VERY DRAFT

## Install galaxy roles
```
    ansible-galaxy install -r requirements.yml
```

## Provision Infrastructure components

The APIMon consists of 4 components:
 - bastion - bastion host for the infrastructure with floating IP
 - executor - host running jobs and telegraf (for metrics forwarding)
 - influxdb - an InfluxDB instance as a TimeSeries DB
 - grafana - instance of Grafana, which shows gathered metrics

Inventory must be prepared, before the infrastructure can be provisioned.

```
    ansible-playbook -i inventory/production playbooks/install/provision_infra.yaml
```

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

Now we can bootstrap/deploy hosts and execute:
```
  ansible
```

Playbooks:
 - install/bootstrap.yaml - provisions `server_common` role to all inventory hosts (especially to be able to access hosts behind bastion, mount attached volumes to required places and installs influxdb and grafana.
 - install/install_influxdb.yaml - included in the bootstrap.yaml. Indivudial steps for influxdb provisioning (installation, creation of admin user and apimon database). Users for telegraf and grafana are not created in this step.
 - install/install_grafana.yaml - included in the bootstrap.yaml. Individual steps for grafans provisioning (installation). Provisioning stuff is mounted into the container running grafana, but it is intended, that datasources are installed separately by "connection" another instance of influxdb into the map.
 - install/install/executor.yaml - included in the bootstrap.yaml. Individual steps for executor host provisioning. It includes local telegraf container (forwards influxdb writes to real InfluxDB) and the executor itself.
 - install/connect_influx_to_grafana.yaml - Creates a read-only user for grafana on a specific (user-input) influxdb instance and provision corresponding datasource to the grafana. A random password is generated for that and not really saved anywhere (except datasource itself).

## Developer setup

It is possible to use tools for development purposes locally with the help of docker-compose (P.S. minishift/minikube would be nice to have)
In order to start it prepare inventory by copying testing inventory folder into something useful (please note testing inventory is saved in git, therefore please do not place any sensitive information. Inventory/production is excluded by gitignore not to accidentially leak data) and modify data as you need (especially cloud credentials in the clouds.yaml must be real).
After this step is done you can start stack by running:
```
    docker-compose up
```

This will build and start 4 containers. Executor will start executing test scenarios and populate InfluxDB. Grafana instance is listening on the localhost port 3000 and can be used to visualize data (default access credentials: 'admin:foobar').
