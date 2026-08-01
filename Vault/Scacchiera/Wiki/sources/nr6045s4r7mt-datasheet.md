---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
source_file: "Datasheets/NR6045S4R7MT_C42370396.pdf"
source_title: "NR6045S4R7MT manufacturer datasheet"
publisher: "Magnetsyc"
---

# NR6045S4R7MT datasheet

This source binds [NR6045S4R7MT](../entities/nr6045s4r7mt.md) to supplier order
code `C42370396`. It is used by hub L1 (4.7uH).

[mpn::NR6045S4R7MT] [order_code::C42370396]
[manufacturer::Magnetsyc] [footprint::Chessboard:NR6045S]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: inductance, tolerance, rated or saturation current, DC resistance, self-resonance, temperature range and package dimensions.
- Exact selected limits: 4.7 uH plus or minus 20 percent, 34 mOhm maximum DCR, 4.97 A minimum saturation, 3.3 A minimum thermal current, 6 x 6 x 4.5 mm body and 1.7 x 5.7 mm pads.
- Datasheet locator: electrical characteristics, ratings and dimensions tables.
- Simulation treatment: analytical, valid only for
  lumped model with datasheet tolerance, bias, ESR, DCR and temperature corners.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Temperature and sequencing data, read 2026-08-01

The header gives the operating temperature range as -40 to +125 degrees Celsius *including self
temp. rise*. Note 1 dates all test data to a 20 degree ambient, note 3 defines Isat as the current
at which inductance drops about 30 percent, and note 4 defines Irms as the DC current causing a
40 degree rise from that 20 degree ambient. Those three fix the coil's thermal corner: at 3.30 A
it sits 40 degrees hot, and below that the rise falls with the square of the current.
