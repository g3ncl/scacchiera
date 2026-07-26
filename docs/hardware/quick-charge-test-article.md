# Quick-charge test article

This document defines the low-cost article proposed to measure the battery and charging risks that
cannot be closed from controller data sheets. It does not qualify the article as a final hub
subassembly or authorize an order before the applicable gates in
[simulation-workflow.md](../simulation-workflow.md) pass.

## Article

The candidate is one MakerMind RBS18634 module, EAN `4251755818419`, listed by
[Roboter-Bausatz](https://www.roboter-bausatz.de/p/sw6106-usb-c-pd-18w-schnelllade-modul-1s-mit-bms)
at 6.76 EUR including VAT on 2026-07-26. It uses the SW6106 controller with one protected 4.2 V
Li-ion cell or parallel 1S assembly. The intended battery article is a protected assembly based on
one Molicel INR-21700-M65A cell with a 103AT-compatible thermistor bonded to the cell.

The module sheet allows up to 4 A charge current and recommends a separate protection board rated
for at least 4 A. The SW6106 data sheet sets 2.5 A from 5 V input and 4 A above 5 V, supports PD
input at 5 V, 9 V, and 12 V, and includes an NTC input. The module sheet does not prove that its NTC
input is exposed or connected. That must be established by inspection before energizing a cell.

Vault evidence: [RBS18634 module sheet](../../Vault/Scacchiera/Datasheets/RBS18634_4251755818419.pdf),
[SW6106 data sheet](../../Vault/Scacchiera/Datasheets/SW6106_C406803.pdf), and
[module evaluation](../../Vault/Scacchiera/Wiki/synthesis/quick-charge-module-evaluation.md).

## Unknowns measured

- Whether the exact received revision connects a battery thermistor to SW6106 NTC rather than
  grounding that pin.
- Sustained battery current and module temperature from a compliant 9 V PD source.
- Time from 10 to 80 percent and from 10 percent to normal termination at 20 to 25 degrees Celsius.
- Whether a representative hub load remains powered without reset during source insertion,
  negotiation, fallback, and removal.
- Charge current and temperature while the representative hub load is active.

## Equipment and record

Use a USB-C PD source and cable rated for at least 9 V and 2 A, a PD protocol meter, a four-wire
battery-current measurement or characterized shunt, two temperature probes, an oscilloscope across
the 5 V output, and a programmable load reproducing the hub profile. Record article photographs,
PCB markings, dimensions, wiring, protection-board identity, instrument models and calibration,
ambient temperature, raw time series, and measurement uncertainty under a unique article ID.

## Acceptance boundary

The article is useful if it sustains the battery's qualified charge rate without exceeding the
temperature limits in [criteria.yaml](criteria.yaml), and its idle cycle meets both functional
charge-time limits. Output interruption is a recorded result, not a waived failure. Even if every
measurement passes, the article does not satisfy final V1 because its component BOM, layout,
protection thresholds, and revision control are unpublished. It can calibrate V3 models and decide
whether an equivalent module architecture is viable.
