---
type: synthesis
date_updated: 2026-07-30
tags:
  - wiki/synthesis
  - wiki/power
  - wiki/battery
---

# Battery format and power module alternatives

Would a flat cell fit the player rail, which lithium format is cheapest, and is there a cheaper or
better shaped alternative to [[pisugar3-plus]]? Asked because that module overhangs the rail by
seven millimetres, which [[commercial-power-subsystem-selection]] left as an open V7 risk.

**Outcome, 2026-07-29.** No module is bound any more. The hub is built against
[[../../../../docs/hardware/power-module-interface.md|a written contract]] instead, so the answers below
are selection input rather than a decision, and the width limit the survey found became a mandatory
property of that contract.

## What the enclosure actually allows

The binding constraint is width, not thickness. From
[[../../../../docs/functional/physical.md|the physical spec]]: player rails are 50 mm, body height
32 mm before feet, top stack at most 1.75 mm, and the sensing PCB is 1.0 mm. Subtracting the top
stack, the air gap, the sensing board and an enclosure floor leaves roughly 24 to 26 mm of usable
height under a rail, against about 46 mm of usable width, which is what the hub itself occupies.
Rail length is not scarce: each player rail is 310 mm long and the hub, at 162 mm, is the only thing
in one of them.

So height rules nothing out. An 18650 at 18.4 mm diameter fits, a 21700 at 21.2 mm fits only if the
holder walls are thin, and any pouch under about 12 mm is comfortable.

[usable_rail_width_mm::46] [usable_rail_height_mm::24] [free_rail_length_mm::148]

## Current 21700 decision

The [[inr-21700-m65a]] proves that a single large cylindrical cell can meet the electrical and
geometric target, but it is not selected. [NKON](https://www.nkon.nl/en/molicel-inr21700-m65a-6500mah-26a.html)
reported the exact flat-top cell out of stock on 2026-07-30, and
[Akkuparts24](https://www.akkuparts24.de/https/wwwakkuparts24de/Molicel-INR21700-M65A-6500mAh-26A-LiIon-Akku-Zelle)
offered only a September preorder. Its filed one-page sheet gives
a 71.0 mm maximum height while Molicel's product page says 70.2 mm, so the design uses the larger
envelope and keeps the source contradiction open.

The more important boundary is the pack, not the can. Molicel's newer tentative approval sheet
requires a protection circuit and recommends direct FET cutoff of both charge and discharge on
cell overtemperature. The hub's independent thermistor window controls charging only. A qualified
assembly therefore still needs a cell-bonded 1S protector with NTC, back-to-back FETs, voltage,
charge-current, discharge-current, and short-circuit protection, plus welded tabs and insulation.
[ABLIC's S-82D1A family](https://www.ablic.com/en/semicon/datasheets/power-management-ic/lithium-ion-battery-protection-ic/s-82d1a/)
demonstrates this architecture, but no exact suffix or pack assembler is bound. Adding an invented
generic protection board would not close V1.

Two European assemblers are plausible quote candidates, not selected suppliers.
[Eltec](https://www.elteconline.com/en/about-us/) advertises custom battery packs from Italy, while
[ANV Production](https://anvproduction.pl/en/battery-packs/) advertises 21700 pack assembly,
prototypes, and small-to-medium production runs from Poland. A useful response must identify the
exact cell and protection circuit, both temperature cutoffs, voltage and current thresholds,
thermistor, interconnect, insulation, connector, lead gauge, assembly drawing, test record, and
transport evidence. Price or availability alone cannot close V1. Neither company has been
contacted.

## The overhang is the cell, not only the board

The PiSugar assembly is 65 x 57 mm, but its cell alone is the LP955465 at 9.5 x 54 x 65 mm. Both
exceed the 46 mm the rail offers, so reshaping the electronics without reshaping the cell would not
have solved it. A pouch narrower than 46 mm, roughly 10 mm thick and 100 to 120 mm long, reaches the
same 18 to 20 Wh and fits, because length is the dimension the rail has to spare.

The LP955465 is a purchasable standard part with its PCM and a JST PHR-2 lead, rated 2.5 A charge and
5 A discharge over 500 cycles. It ships without an NTC, which is exactly why the hub carries its own
cell-bonded sensor and the [[fail-safe-cell-temperature-window]].

## Format economics

| Format | Energy | Cost per Wh | What it costs elsewhere |
| --- | --- | --- | --- |
| 18650 cylindrical | 10 to 12 Wh | lowest | holder or spot welding, separate PCM, 18.4 mm of height |
| 21700 cylindrical | 17 to 19 Wh | lowest, near 18650 | same, plus 21.2 mm of height |
| LiPo pouch 1S | any, by size | roughly double | none: arrives with PCM, leads and connector |

Cylindrical cells are the cheapest per watt-hour and 18650 and 21700 now sit close to each other,
with 21700 needing fewer cells for a given pack. That advantage is a volume argument. On a single
18 Wh pack the absolute difference is a few euro, while the pouch removes a holder, a separate
protection board, a spot welder, and a centimetre of height. For one or two boards the pouch wins on
everything except headline cost per watt-hour. [cheapest_per_wh::21700] [best_fit_here::1S pouch]

## Module alternatives

Every candidate below provides charging, a 5 V converter and I2C state; the differences are size,
included cell, and how much evidence they hand back to us.

| Module | Size | Cell | 5 V out | Price | Fits the rail |
| --- | --- | --- | --- | --- | --- |
| [[pisugar3-plus]] | 65 x 57 mm | 5000 mAh included | 3 A | 49.99 USD | no, 57 mm |
| DFRobot UPS HAT for Pi Zero | 65 x 30 mm | none, PH2.0 lead | 2 A | 19.90 USD | yes |
| Waveshare UPS HAT (B) | 85 x 56 mm | 2 x 18650, none included | 5 A | 25.95 USD | no, 56 mm |
| Waveshare UPS HAT (E) | Pi HAT class | 4 x 21700, none included | 6 A | not priced here | no |

The earlier survey in [[commercial-power-subsystem-selection]] rejected DFRobot's DFR1026, SunFounder
PiPower 5 and Waveshare UPS Module Mini. Two of those reasons have weakened: the Pi Zero UPS HAT
carries a Maxim fuel gauge, so state of charge is no longer ours to build, and a separately chosen
pouch fixes the capacity objection that ruled out the Mini.

## The unbundled option

Buying the module and the cell separately is cheaper than the bundle and fits the rail:

`5 V USB in -> 65 x 30 mm UPS module -> 5 V out -> hub` with a rail-shaped 1S pouch on the module's
PH2.0 lead. About 20 USD plus 15 to 20 EUR of cell, against 49.99 USD, and no seven-millimetre
overhang.

What it costs instead is evidence. Uninterrupted handover is the property the whole subsystem exists
for and the product page does not state it, so V8 would have to measure output continuity across
source insertion and removal rather than cite it. Mechanical cell protection and retention become
ours. The 2 A output is adequate against the board's worst case (448 mA of light bars, a 382 mA
ESP32-C6 peak through the buck, reader, displays and matrix, roughly 1.0 to 1.3 A at 5 V) but with
less headroom than 3 A.

[unbundled_cost_eur::35 to 40] [bundled_cost_usd::49.99]

## Screening criterion: power-bank auto-standby

Most cheap charger-plus-boost modules are built on power-bank controllers, and a power bank is
supposed to switch itself off when nothing is drawing from it. The IP5306 is the common example: its
boost output collapses after the load stays under about 45 to 50 mA for 32 seconds.

The board sleeps after twenty idle minutes under `GAME-IDLE-SLEEP`, drawing far less than that, so a
module with this behavior would cut power roughly half a minute into every sleep. The I2C variant can
disable it by setting bit 1 of register 0, but that turns a product requirement into a firmware write
against a register map the manufacturer does not publish in a filed data sheet.

Every candidate in this class must therefore answer: does the output stay up at a few milliamps
indefinitely, and if that depends on a register write, does the setting survive a brownout and a
power cycle? This applies to the DFRobot module above as much as to any IP5306 board.

[screening::light-load auto-standby] [sleep_current_vs_threshold::far below 45 mA]

## Open questions before this could be selected

- Uninterrupted output during source insertion and removal, unstated by the vendor.
- A pouch part number at or under 46 mm wide with 18 Wh and a filed transport report.
- An in-stock exact cylindrical cell or protected pouch with consistent dimensional evidence.
- A qualified pack assembler and exact protector that disconnects both directions on cell
  overtemperature, not only a charger-side temperature gate.
- Retention and impact protection for a bare pouch inside a printed rail, with the ventilation the
  cell's own safety instructions require either way.
