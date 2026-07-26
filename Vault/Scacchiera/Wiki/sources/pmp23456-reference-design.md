---
type: source-summary
date_updated: 2026-07-26
tags:
  - wiki/source
  - wiki/power
---

# PMP23456 reference design

Texas Instruments' November 2024 test report for a complete [[usb-c-pd-fast-charging|USB-C PD
single-cell charger]] using [[tps25730s]] and [[bq25638]]. The immutable report is
[[../../Clippings/TI-PMP23456-test-report.pdf]].

## Measured behavior

The reference negotiates either 5 V/3 A or 9 V/3 A and provides battery plus system power through
an NVDC power path. TI configured the reference for 3 A total output. At 5 V input, its published
charge-efficiency table reaches 92.817 percent at 3.035 A into a 4.43 V simulated battery load. The
report also includes 9 V system and charge efficiency, 3 A thermal images, startup, ripple, and load
transient measurements. See report sections 1 through 3.

[pd_contracts::5V3A-or-9V3A] [measured_charge_efficiency_percent::92.817]

## Reuse boundary

The chessboard may reuse the topology and validated operating modes, but a higher 4 A charge target
requires its own inductor, copper, thermal, input-limit, and simultaneous-system-load validation.
The reference is evidence that the architecture works, not evidence that an altered board passes.
