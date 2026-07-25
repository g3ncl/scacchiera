---
type: source-summary
tags:
  - wiki/source
date_updated: 2026-07-25
source_file: "Datasheets/SK6812MINI-E_C5149201.pdf, Datasheets/SK68XX-MINI-E_family_rev08.pdf"
source_title: "SK6812MINI-E rev 02 and SK68XX MINI XX rev 08 specifications"
publisher: Dongguan OPSCO Optoelectronics
---

# SK68XX MINI-E LED datasheets, rev 02 and rev 08

Two OPSCO documents covering the addressable LED family the
[light bar](../../../../docs/hardware/lightbar.md) uses. Filed together because
**they disagree with each other**, which matters for the footprint. See
[[sk6805mini-e]] for what the project concluded.

## Document rev 02, "SK6812MINI-E"

[mpn::SK6812MINI-E] [lcsc::C5149201] [package_mm::3.2x2.8x1.78]

- Titled "SK6812MINI-E, 3.2x2.8x1.78 mm 0.2W Intelligent external control
  surface mount SMD LED (MSL:5a)".
- **Pin configuration (section 5): 1 VDD, 2 DOUT, 3 GND, 4 DIN.** Top view
  places VDD top left, DOUT bottom left, GND bottom right, DIN top right.
- Section 7 states the naming covers the "68 series IC 5/12MA current version"
  in the "3.2x2.8x1.78mm package outline", so one package, two drive currents.
- Section 9 tabulates both variants side by side:

| Colour | SK6805MINI-E, 5 mA | SK6812MINI-E, 12 mA |
| --- | --- | --- |
| Red | 620-630 nm, 100-200 mcd | 620-625 nm, 400-700 mcd |
| Green | 520-535 nm, 400-700 mcd | 520-530 nm, 1000-1500 mcd |
| Blue | 460-475 nm, 50-100 mcd | 460-470 nm, 200-400 mcd |

## Document rev 08, "SK68XX MINI XX"

[package_mm::3.5x3.7]

- **Pin configuration: 1 DIN, 2 VDD, 3 DOUT, 4 VSS.** Different from rev 02.
- Mechanical drawing gives a 3.5 ± 0.1 by 3.7 ± 0.1 mm body, a 3535 outline,
  not rev 02's 3.2 x 2.8.
- Recommended PCB pads span 4.3 mm horizontally (1.5 + 0.6 + 2.2 across the top,
  2.4 + 0.6 + 1.3 across the bottom).
- Section 9 repeats the same 5 mA / 12 mA optical split as rev 02.

## Electrical values common to both (sections 8, 10, 11)

| Parameter | Value |
| --- | --- |
| Supply voltage VDD | +3.7 to +5.5 V |
| Logic input voltage | -0.5 to VDD+0.5 V |
| VIH | 0.7 x VDD min |
| VIL | 0.3 x VDD max |
| Chip supply voltage typ | 5.2 V |
| PWM frequency | 1.2 kHz |
| **Static power consumption IDD** | **1 mA typ** |
| Data rate fDIN | 800 kHz typ |
| DOUT delay TPLH/TPHL | 500 ns max |
| Output rise/fall | 100 ns at IOUT 13 mA |
| Operating temperature | -40 to +85 C |
| ESD HBM | 4 kV |

[channel_current_ma_sk6805::5] [channel_current_ma_sk6812::12] [idd_ma::1]
[vih_fraction::0.7] [data_rate_khz::800]

VIH at 0.7 x VDD is 3.5 V on a 5 V rail, which is why the hub drives the chain
through a 5 V AHCT buffer rather than straight off a 3.3 V GPIO.

## The contradiction, stated plainly

Rev 02 and rev 08 give different pinouts for nominally the same family, and
different package outlines. They are best read as two different packages: rev 02
is the 3.2 x 2.8 mm MINI-E, rev 08 the 3.5 x 3.7 mm 3535. The project binds the
rev 02 pinout because LCSC C5149201's manufacturer and MPN match that document
exactly. Nothing here resolves which document the delivered
[[sk6805mini-e]] reel follows, and that is recorded as an open risk rather than
assumed away.

Related: [[jlcpcb]], [[jlcpcb-basic-part-sourcing]]
