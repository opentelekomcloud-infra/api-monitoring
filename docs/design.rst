API Monitoring: High-Level Design
=================================

:Authors:
    Artem Goncharov (artem.goncharov@t-systems.com);
    Nils Magnus (nils.magnus@t-systems.com);
    Vladimir Hasko (vladimir.hasko@t-systems.com);
    Tino Schreiber (tino.schreiber@t-systems.com)
:Copyright: 2019 by Open Telekom Cloud (https://open-telekom-cloud.com/)
:Version: 1.0.1 as-of 2019/07/01 (work in progress)
:Availability: public

This document describes the design for a **service that monitors the service
availability of OpenStack based cloud APIs**. This service is useful for
operators and users of clouds alike, since it visualizes the availability of
the manifold cloud services. It also helps to mitigate outages and other
incidents. The service is called henceforth API-Monitoring or APIMon for short.

While it was developed for the Open Telekom Cloud, all designs and
implementation described in this document apply to any upstream compatible
OpenStack cloud instance unless otherwise noted.


Current Situation
-----------------

A full-scale public cloud setup is a complex piece of software, comprising of
many API driven services with a lot of functions and even more attributes.
Outages in particular services are difficult to detect in a timely manner if
monitored manually.

This service mitigates the delayed detection of outages and helps to detect
issues for both users and operators of a cloud offering.


Acceptance Criteria
-------------------

Since "service", "availability", "incidents", and "outages" are terms that are
hard to define, this is a list of criteria the API-Monitoring should implement:

* The API-Monitoring **covers all relevant services** of a cloud setup from a
  user perspective.
* The API-Monitoring checks for the **availability of the service endpoints**.
* The API-Monitoring verifies if the **actual services** behind the endpoints
  are really available and are performing the desired action.
* The checks of the API-Monitoring are **easy to write** and use a wide-spread
  language to describe test cases.
* The checks of the API-Monitoring are **easy to extend** and not built in the
  monitoring itself. The are outfactored to a separate repository that can be
  maintained and updated independently from the test infrastructure.
* The API-Monitoring executes realistic user-scenarios, comprising a sequence
  of single steps reflecting actual use cases.
* The API-Monitoring itself is **highly available** even if parts, or the whole
  cloud is not available. This includes any cloud service and the networking up
  to and including the upstream exchange point with the Internet service
  provider.


Out of Scope
------------

The following items are out of scope (while some of them are technically possible):

#. **No performance monitoring:** The API-Monitoring does not measure degradations
   of performance per se. So measuring the access times or data transfer rates of
   an SSD disk is out of scope. However, if the performance of a ressource drops
   under some threshold that is considered as equivalent to non-available, this is
   reported.
#. **No application monitoring:** The service availability of applications
   that run on top of IaaS or PaaS of the cloud is out of scope.
#. **No view from inside:** The API-Monitoring has no insights and is only uses public
   APIs of the monitored cloud. It requires thus no administrative permissions
   on the backend. It can be, however, deployed additionally in the backplane
   to monitor additionally internal APIs.
#. **No synthetic workloads:** The service is not simulating any workloads (for
   example a benchmark suite) on the provisioned resources. Instead it measures
   and reports only if APIs are available and return expected results with an
   expected behaviour.


Solution Approach and Architecture
----------------------------------

The API-Monitoring project permanently supervises the public APIs of an
OpenStack-based platform. To do that, it sends requests repeatedly to the API.
The requests are grouped in so-called scenarios, mimicking real-world use cases.
These use cases are implemented as Ansible playbooks. This makes it easy to
extend the API-Monitoring for other use cases like monitoring the provisioning
of extra VMs or deploying extra software.

The actual metrics for the monitoring are collected implicitly; developers of
scenarios are not required to take care of that. The flow of monitored data
is organized in a pipeline. It collects metric data on individual client
instances (Executor), aggregating them on the clients (Telegraf), storing
and processing data (InfluxDB), and finally visualizing (Grafana) or
alerting under some conditions.

The architecture can be replicated for several independent **environments**. Each
of it collects individually data based on the same metrics. A visualization or
alerting component may or may not combine the environment data. Examples for
environments could be production and testing setups, but also reflect different
origins of the scheduled probes. This is especially important as it is not
advisable to rely on a monitoring infrastructure that monitors itself.


Components
----------

An `Executor` component is the core of the system, scheduling continously test
scenarios written as Ansible playbooks. The scenarios are collected in a Git
repository and updated in real-time. In general the playbooks do not need take
care of generating data implicitly. Since the API related tasks in the playbooks
rely on the `Python OpenStack SDK`_ (and its `OTC extensions`_), metric data
generated automatically by an `logging interface`_ of the SDK. This mechanism
can be augmented by other sources and formats. 

The metrics are collected by a `Telegraf`_ component. It is responsible for
forwarding data to a `InfluxDB`_ instance, to store it as time series data.
This data is unique for each environment. Its metrics are the same, but the
values may be different for different environments (i.e. duration of server
creation from inside the cloud and from outside of the cloud). It is later then
being consumed by a clustered `Grafana`_ to visualize the monitoring results.

::

   +-----------------------------------------------------------------------------------------------+
   | Environment 1                                                                                 |
   |                                                                                               |
   | +----------+       +----------+       +----------+            +---------+       +-----------+ |
   | | Executor |       |          |       |          |            |         |       |           | |
   | | Ansible/ |------>| Telegraf |------>| InfluxDB |----------->| Grafana |<----->|           | |
   | | OS SDK   |       |          |       |          |            |         |       |           | |
   | +----------+       +----------+       +----------+           >+---------+       |           | |
   |                                                   \         /                   |           | |
   |                                                    \       /                    |           | |
   +-----------------------------------------------------\-----/---------------------|           |-+
                                                          \   /                      |           |  
                                                           \ /                       |           |  
                                                            X                        | Clustered |  
                                                           / \                       | Grafana   |  
                                                          /   \                      | Database  |  
   +-----------------------------------------------------/-----\---------------------|           |-+
   |                                                    /       \                    |           | |
   |                                                   /         \                   |           | |
   | +----------+       +----------+       +----------+           >+---------+       |           | |
   | | Executor |       |          |       |          |            |         |       |           | |
   | | Ansible/ |------>| Telegraf |------>| InfluxDB |----------->| Grafana |<----->|           | |
   | | OS SDK   |       |          |       |          |            |         |       |           | |
   | +----------+       +----------+       +----------+            +---------+       +-----------+ |
   |                                                                                               |
   | Environment 2                                                                                 |
   +-----------------------------------------------------------------------------------------------+

    Schematic Architecture

The origin of the requests to the APIs affects the availability results. The
results returned by an API may depend on if the request was made inside the
cloud itself or originates from outside. The API-Monitoring covers thus also
situations where, when tested from inside, a cloud platform is performing
well, but appears unavailable when tested from outside the platform over
the Internet. This is the reason why at least one environment needs to be
located outside and one inside the monitored cloud platform. This approach
assures availability of the alerting and the dashboards components even in
case of a platform outage.


Executor
--------

The `Executor` component of an API-Monitoring environment is responsible for
scheduling and executing individual jobs defined as Ansible playbooks
collected in an external repository. It is implemented as a process,
periodically scanning the repository. For each scenario playbook it forks
a process, which schedules it for continous execution interrupted by some
delay, if required. Those processes generate metrics in two ways:

- The Ansible playbook internally invokes method calls to OpenStack SDK
  libraries. They in turn generate metrics about each API call they do.
  This requires some special configuration in the `clouds.yaml` file
  (currently exposing metrics into statsd and InfluxDB is supported).
  For details please refer to the `config documentation`_ of the
  OpenStack-SDK.

- Ansible plugins may expose additional metrics (i.e. whether the overall
  scenario succeded or not). Since sometimes it is not sufficient to know
  only the timings of each API call, Ansible callbacks are utilized to
  report overall execution time and result (whether the scenario succeeded
  and how long it took).


Telegraf
--------

The `Executor` is exposing metrics, but where do they go? One option is to
place an instance of `Telegraf` to accept metrics from the `Executor` and serve
as a proxy to place data (with potentially format conversion) into a required
destination. In our case it acts as a proxy inserting InfluxDB-format data into
a real database, which might require special access. In addition it immediately
gives possibility to expose data to a `Prometheus` instance (what is not
currently used).


InfluxDB
--------

The community edition of InfluxDB is used to store data of each individual
API-Monitoring environment. It receives data from `Telegraf` and exposes it to
`Grafana`.

Since it is exposed to the internet, TLS must be enabled.


Grafana
-------

Having clustered `Grafana` allows permanently monitoring the platform from
different origins. Performance of the server provisioning from inside of the
platform can be compared to inside of an instance already running in the cloud
(you have an instance in cloud and would like to create another one from it)
with doing that through a real internet connection. This helps to detect
potential problems with API-gateways, Internet channels (an issue we have seen
ourselves). In `Grafana` we can then implement dashboard with panels showing
the same measures from different datasources and immediately see a problem.

Grafana is a component of the API-Monitoring requiring a proper failover. It
can be implemented in different ways with a real load-balancer instance, DNS
with load-balancer, DNS round-robin, etc. We currently do this as a DNS with
round-robin switching between different environments. In this case a clustered
Grafana setup (with a clustered DB in the backend) should be used.

Since it is exposed to the internet, TLS must be enabled.


InfluxDB vs. Prometheus
-----------------------

Prometheus is a nice tool, but the nature of the API-Monitoring from the users
point of view is to periodically try to invoke API. Those calls by nature might
have different duration and trying to estimate some average value for the last
5 minutes is a wrong approach. Instead what we do is we generate events. Those
events should be saved in any kind of database (preferably time-series DB).


Technical Considerations
------------------------


.. References

.. _`Python OpenStack SDK`: https://docs.openstack.org/openstacksdk/latest/
.. _`OTC extensions`:       https://python-otcextensions.readthedocs.io/en/latest/
.. _`logging interface`:    https://github.com/openstack/openstacksdk/commit/c8b96cddd3d65b9b79788d93e72fe499f07ffae0
.. _`config documentation`: https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html#config-files
.. _Telegraf:               https://www.influxdata.com/time-series-platform/telegraf/
.. _InfluxDB:               https://www.influxdata.com/products/influxdb-overview/
.. _Grafana:                https://grafana.com/grafana
