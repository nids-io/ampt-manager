# ampt-manager

Management service for the AMPT passive network tools monitor

AMPT is a practical framework designed to aid those who operate network IDS
sensors and similar passive security monitoring systems. A tailored approach
is needed to actively monitor the health and functionality of devices that
provide a service based on capturing and inspecting network traffic. AMPT
supports these types of systems by allowing operators to validate traffic
visibility and event logging on monitored network segments. Examples of
systems that can benefit from this type of monitoring are:

* [Suricata IDS][suricata]
* [Snort IDS][snort]
* [Bro IDS][bro]
* [Moloch][moloch]

**ampt-manager** is the core component in the AMPT framework. It is simple to
deploy and provides the following:

* Web-based management console 
* Central point for configuration and management of AMPT nodes, including:
  * Monitored network segments
  * AMPT generator nodes
  * AMPT monitor instances
* State of network visibility from the standpoint of monitored segments
* Logging and accounting of events related to monitoring process
* Configurable alerting/notifications when monitors for configured segments
  encounter degraded visibility

Other AMPT components include:

* [ampt-generator][ampt_generator] -  Health check packet generator for the
  AMPT passive network tools monitor
* [ampt-monitor][ampt_monitor] -  Sensor alert monitor core package for the
  AMPT passive network tools monitor

## Installation and usage

See the [Wiki](https://github.com/nids-io/ampt-manager/wiki/) for further
documentation.


[suricata]: https://suricata-ids.org/
[snort]: https://www.snort.org/
[bro]: https://www.bro.org/
[moloch]: https://github.com/aol/moloch
[ampt_generator]: https://github.com/nids-io/ampt-generator
[ampt_monitor]: https://github.com/nids-io/ampt-monitor
[wiki]: https://github.com/nids-io/ampt-manager/wiki/

