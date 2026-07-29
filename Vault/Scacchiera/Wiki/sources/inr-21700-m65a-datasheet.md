---
type: source-summary
date_updated: 2026-07-30
tags:
  - wiki/source
  - wiki/battery
---

# INR-21700-M65A product data sheet

Manufacturer product data sheet for the [[inr-21700-m65a]] cylindrical lithium-ion cell considered
for the chessboard's 5 V, 10 W power system. The immutable source is
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
| Height | 71.0 mm maximum | Physical characteristics |
| Mass | 74.5 g | Physical characteristics |

[capacity_ah::6.5] [standard_charge_a::6.5] [diameter_mm::21.7] [height_mm::71.0]

## Boundary

This source describes a bare cell, not a protected consumer battery. It does not justify fitting an
unprotected loose cell. The product needs a qualified assembly with independent protection, a cell
thermistor, insulated interconnect, and a connector rated for the configured current.

Molicel's product page reported 70.2 mm height while this filed sheet reports 71.0 mm maximum. The
design uses 71.0 mm and keeps the contradiction open. A newer 2026 tentative approval sheet exposed
through NKON adds pack-protection details, but its download returned HTTP 403 outside the browser
and several fields are explicitly TBD or estimated, so it is not treated as filed release evidence.
