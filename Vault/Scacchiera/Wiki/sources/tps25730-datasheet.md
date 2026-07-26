---
type: source-summary
date_updated: 2026-07-26
tags:
  - wiki/source
  - wiki/usb-c
---

# TPS25730 data sheet

Texas Instruments data sheet for the [[tps25730s]] autonomous sink-only USB Type-C Power Delivery
controller. The immutable source is [[../../Datasheets/TPS25730SRSMR_TI.pdf]].

## Design-dependent values

The controller includes Type-C attach detection, dead-battery pull-downs, the PD policy engine, and
resistor-programmed configuration. The S variant uses a 32-pin QFN and controls an external sink
power path. Its VBUS input range reaches 22 V in normal operation and its sink path controls support
PD current levels. CAP_MIS reports that the negotiated source cannot satisfy the configured power
requirement. See data-sheet sections 1, 5, 6, 8, and 9.

The PD controller uses the CC pins. USB 2 data can remain routed directly between the receptacle and
ESP32-C6 while the controller negotiates power independently.

[variant::TPS25730S] [package::RSM-32-QFN] [role::sink-only]

## Configuration boundary

The resistor strap must be generated from TI's published configuration table and checked against
the exact [[pmp23456-reference-design|PMP23456]] 5 V/3 A and 9 V/3 A contract behavior. An assumed
strap or a firmware-only promise is not release evidence.
