---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
source_file: "Datasheets/CDMC8D28NP-1R2MC_C17268233.pdf"
source_title: "CDMC8D28NP-1R2MC manufacturer datasheet"
publisher: "Sumida"
---

# CDMC8D28NP-1R2MC datasheet

This source binds [CDMC8D28NP-1R2MC](../entities/cdmc8d28np-1r2mc.md) to supplier order
code `C17268233`. It is used by power L2 (1.2uH).

[mpn::CDMC8D28NP-1R2MC] [order_code::C17268233]
[manufacturer::Sumida] [footprint::Chessboard:CDMC8D28]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: inductance, tolerance, rated or saturation current, DC resistance, self-resonance, temperature range and package dimensions.
- Exact selected limits: 1.2 uH plus or minus 20 percent, 7 mOhm maximum DCR, 12.2 A saturation current, 12.9 A thermal current and 8.7 by 8.3 by 3.0 mm maximum body.
- Datasheet locator: electrical characteristics, ratings and dimensions tables.
- Simulation treatment: analytical, valid only for
  lumped model with datasheet tolerance, bias, ESR, DCR and temperature corners.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Temperature and sequencing data, read 2026-08-01

The features list gives the operating temperature range as -40 to +125 degrees Celsius including
the coil's self temperature rise, and note 3 defines the temperature-rise current as the DC
current giving a 40 degree rise at a 20 degree ambient. Same convention as the hub's coil, so the
two are cornered the same way.
