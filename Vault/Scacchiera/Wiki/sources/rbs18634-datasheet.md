---
type: source-summary
date_updated: 2026-07-26
tags:
  - wiki/source
  - wiki/power
---

# RBS18634 module data sheet

The seller-issued three-page product sheet for the [[rbs18634]] SW6106 USB-C PD 18 W module. The
immutable source is [[../../Datasheets/RBS18634_4251755818419.pdf]].

The sheet identifies MakerMind as manufacturer, EAN `4251755818419`, and the fitted controller as
[[sw6106]]. It specifies one 3.7 V Li-ion or LiPo cell, selectable 4.2 V or 4.35 V termination,
bidirectional USB-C PD, 18 W maximum input or output power, and charge or discharge current up to
4 A. USB-C is bidirectional and USB-A is output-only. See pages 1 and 2.

[module_code::RBS18634] [ean::4251755818419] [maximum_power_w::18]
[maximum_charge_discharge_a::4] [cell_count::1]

The same sheet recommends short, thick battery wiring, cooling at high power, and an external
battery-protection board rated at least 4 A. This recommendation takes precedence over the retail
title's broad `with BMS` wording. The sheet does not identify a battery NTC connector, output
handover time, board dimensions, component BOM, schematic, protection thresholds, or guaranteed
sustained current. Those omissions block treating the module as a final qualified subassembly.
