---
type: source-summary
date_updated: 2026-07-26
tags:
  - wiki/source
  - wiki/power
---

# SW6106 data sheet

English data sheet revision 2.2, May 2022, for the [[sw6106]] bidirectional fast-charge power-bank
controller. The immutable source is [[../../Datasheets/SW6106_C406803.pdf]].

## Relevant limits and behavior

The device integrates a single-cell switching charger, an 18 W synchronous boost converter, USB-C
PD input and output policy, a fuel gauge, port control, and an NTC input. Charge current is 2.5 A
from 5 V input and 4 A when the negotiated input voltage is above 5 V. PD input and output support
5 V, 9 V, and 12 V. See sections 1, 9.1, 9.3, and 9.5.

With a 103AT thermistor, charging stops below 0 degrees Celsius or above 50 degrees Celsius and is
reduced between 0 and 10 degrees Celsius and between 40 and 50 degrees Celsius. The NTC pin may
instead be grounded to disable this protection, so the controller feature alone does not prove that
any particular module monitors its battery. See section 9.1.

The controller can charge the battery while supplying an external device. When more than one port
is active it permits only 5 V input and output. Its Type-C and boost paths also use attach and
light-load detection. The document does not specify uninterrupted system-rail handover during cable
insertion or removal. See sections 9.2 through 9.4.

[maximum_charge_a::4] [charge_at_5v_a::2.5] [maximum_power_w::18]
[supported_pd_input_v::5,9,12] [ntc_profile::103AT]

## Verification boundary

This source describes the controller, not the complete [[rbs18634]] module. Module-level NTC
wiring, protection thresholds, copper temperature, sustained current, output continuity, and exact
revision remain Measured or Assumed until the named article is inspected and tested.
