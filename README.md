CAPCollector&trade;
============
[![Build Status](https://travis-ci.org/CAPTools/CAPCollector.svg?branch=master)](https://travis-ci.org/CAPTools/CAPCollector)


**CAPCollector&trade;** is a server designed to authenticate, sign, aggregate
and forward [Common Alerting Protocol (v1.2)](http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html)
alerts.

Combined with [CapCreator&trade;](https://github.com/CAPTools/CapCreator),
the tools offer an easy-to-use web form for creating and updating alerts,
authentication mechanisms to control alert publishing, a database for recording
published alerts, and endpoints for external users to view and download active
alerts.

It is designed to run on any standard web server, both locally hosted and from
cloud-hosted providers.  See the [documentation](./documentation) folder for
installation instructions.

**Features**

 * Create and reuse standard templates to simplify new alert generation.
 * Required technical fields in the Common Alerting Protocol specification are
 populated automatically to ensure alerts are properly and consistently identified
 and updated.
 * Authentication gives you control over who can officially publish alerts.
 * Built-in support for a serving a feed of active alerts, both as XML and as an
 embeddable HTML widget.
 * Designed to work well on tablets and mobile devices as well as desktops.


**A few notable limits on the current version:**

 * Only one language can be used in a single message (however multiple messages
 can be authored to address multilingual alerting requirements);
 * Only one target area can be specified for an individual alert message (but
 it may include multiple polygons and/or circles); and,
 * All alerts are assumed to be effective immediately; the "effective" and
 "onset" elements are not supported.

The CAP Creator combines two pieces of the [open-source CAPTools™](https://github.com/CAPTools)
project originally created at Carnegie Mellon University by a team lead by Art
Botterell, one of the original designers of the Common Alerting Protocol.

 **CAPTools&trade;**, **CAPCreator&trade;**, **CAPCollector&trade;** and
 **CAPConsumer&trade;** are trademarks of Carnegie Mellon  University.
