---
type: synthesis
date_updated: 2026-07-26
tags:
  - wiki/synthesis
  - wiki/power
  - wiki/battery
---

# Commercial power subsystem selection

The most compact complete solution found is [[pisugar3-plus]], not a copied charger circuit. It
combines an included 18.5 Wh pouch cell, 5 V/3 A input and output, cable-change UPS behavior, I2C
status, charge control, and published cell transport testing in a 65 x 56 mm class assembly.

The alternative DFRobot DFR1026 is much smaller and cheaper, but it leaves the battery selection,
state-of-charge measurement, current measurement, source detection, cable-handover proof, and
mechanical battery protection to the chessboard. SunFounder PiPower 5 provides better power and
current telemetry, but needs a separate 2S battery pack and occupies an 85 x 56 mm board. Waveshare
UPS Module Mini fits the rail width but its specified three 350 mAh cells cannot meet runtime.

The selected system boundary is:

`5 V USB input -> PiSugar 3 Plus -> regulated 5 V -> hub 5 V and 3.3 V buck`

The light bars use the commercial 5 V output through the existing current limiter. A single buck
regulator supplies the ESP32-C6, reader, displays, and matrix at 3.3 V. The hub retains I2C access to
external-power presence, charge enable, battery voltage, percentage, and delayed output shutdown.

The normal source is 5 V/2 A. A 5 V/3 A source is permitted because the module specifies it, but no
USB Power Delivery contract is required. The supplied cell's 2.5 A published charge current and
18.5 Wh energy make a two-to-three-hour complete recharge plausible; V8 records the real curve while
the idle chessboard is attached.

Two constraints remain explicit. The vendor model is 57 mm across its components, seven millimetres
wider than the nominal player rail, so V7 must prove a ventilated service cassette outside the NFC
loop envelope. The module reports charger-chip temperature rather than cell temperature, so V8 must
not close until a cell-temperature interlock is defined and demonstrated. The [[955465-un38-3|UN
38.3 report]] applies to transport tests on the cell, not certification of the completed board.
