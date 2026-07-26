---
type: source-summary
date_updated: 2026-07-26
tags:
  - wiki/source
  - wiki/battery
---

# INR-21700-M65A product data sheet

Manufacturer product data sheet for the [[inr-21700-m65a]] cylindrical lithium-ion cell considered
for the chessboard's [[usb-c-pd-fast-charging|fast-charge power system]]. The immutable source is
[[../../Datasheets/INR-21700-M65A_MOLICEL.pdf]].

## Design-dependent values

| Parameter | Published value | Locator |
| --- | ---: | --- |
| Nominal capacity | 6.5 Ah | Product specification table |
| Nominal voltage | 3.6 V | Product specification table |
| Charge voltage | 4.2 V | Product specification table |
| Discharge cutoff | 2.5 V | Product specification table |
| Standard charge current | 6.5 A | Product specification table |
| Standard charge time | 1.75 hours | Product specification table |
| Charge ambient range | 0 to 60 degrees Celsius | Product specification table |
| Continuous discharge current | 26 A | Product specification table |
| Diameter | 21.7 mm | Physical characteristics |
| Height | 70.2 mm | Physical characteristics |
| Mass | 74.5 g | Physical characteristics |

[capacity_ah::6.5] [standard_charge_a::6.5] [diameter_mm::21.7] [height_mm::70.2]

## Boundary

This source describes a bare cell, not a protected consumer battery. It does not justify fitting an
unprotected loose cell. The product needs a qualified assembly with independent protection, a cell
thermistor, insulated interconnect, and a connector rated for the configured current.
