---
type: source-summary
date_updated: 2026-07-29
tags: [wiki/source, wiki/power, wiki/battery]
---

# BQ25619RTWR data sheet

Texas Instruments data sheet revision F, February 2025, for the [[bq25619rtwr]] 1S switch-mode
charger and NVDC power path. The immutable source is
[[../../Datasheets/BQ25619RTWR_C2864534.pdf]].

## Design-dependent values

| Parameter | Published value | Locator |
| --- | ---: | --- |
| Package | 24-pin 4 x 4 mm WQFN, RTW | Sections 3 and 5 |
| Maximum charge current | 1.5 A | Section 7.3.6 |
| Autonomous default charge current | 340 mA | Table 7-2 |
| PSEL high or low input limit | 500 mA or 2.4 A | Table 7-1 |
| Programmable input-current range | 0.1 to 3.2 A | Electrical Characteristics |
| BATFET resistance | 19.5 mOhm typical, 30 mOhm maximum | Electrical Characteristics |
| BATFET discharge clamp | 5 A minimum, 6 A typical | Electrical Characteristics, ISYS_OCP_Q4 |
| Default input-voltage regulation | 4.5 V | Section 7.3.3.4 |

The device starts autonomously from a battery or input source. Its 500 mA PSEL state is the safe
cold-start choice before a host programs the qualified source and charge limits. The 5 A minimum
battery clamp requires the downstream boost to stop before depleted-cell current reaches it.

[mpn::BQ25619RTWR] [order_code::C2864534] [package::RTW-WQFN-24]
