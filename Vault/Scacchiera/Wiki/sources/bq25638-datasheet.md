---
type: source-summary
date_updated: 2026-07-26
tags:
  - wiki/source
  - wiki/power
---

# BQ25638 data sheet

Texas Instruments data sheet revision B, May 2026, for the [[bq25638]] single-cell switching
charger. The immutable source is [[../../Datasheets/BQ25638YBGR_TI.pdf]].

## Design-dependent values

The device is a 1.5 MHz synchronous buck charger with NVDC power-path management. It accepts 3.9 to
18 V, regulates charge current from 80 mA to 5.04 A in 80 mA steps, and provides a programmable
input-current limit. The input-current register reaches 3.2 A. The lower of the ILIM pin and I2C
setting controls input current. See data-sheet sections 1, 5, 7, and 8.

The TS and TS_BIAS pins support a controlled NTC divider and programmable JEITA behavior. Charging,
input limits, thermal regulation, safety timers, status, and ADC telemetry are available through
I2C. The only package is a 30-ball, 2.07 by 2.36 mm DSBGA.

[maximum_charge_a::5.04] [maximum_input_limit_a::3.2] [maximum_input_v::18]

## Simulation boundary

No distributable transistor-level model was identified. V3 must use a data-sheet-bounded averaged
switching and state-machine model, including input-current regulation, system priority, thermal
foldback, battery temperature regions, safety timers, and the external inductor and capacitor
corners. V8 remains responsible for measured charge time and thermals.
