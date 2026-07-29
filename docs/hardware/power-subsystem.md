# Power subsystem selection

Which fitted power implementation and cell fill the boundary defined in
[power-module-interface.md](power-module-interface.md). That file is the contract; this one records
what is fitted, what was considered, and what still has to be measured.

## Status

**The custom power board is fitted.** It uses BQ25895, TPS61088, TLV809K33, and a
CSD25404Q3/TLV7021 reverse-cell stage while preserving the same contract an optional purchased
module would implement. The mating housings and 18 AWG terminals are exact; the wire, qualified
crimp or pre-crimped leads, complete harnesses, and protected battery assembly are not bound, so V1
remains open.

Binding one is a V1 action: file its manufacturer documentation in the vault, record the exact
product and revision, and check it against every mandatory property in the interface.

## Candidates

| Module | Verdict |
| --- | --- |
| PiSugar 3 Plus | Meets the electrical contract, including its own 5000 mAh cell, but is 57 mm across against the 46 mm the rail allows. Its cell alone is 54 mm, so reshaping the electronics would not fix it. |
| Small UPS or charger-boost modules with a fuel gauge | Fit the width and cost far less, but hand back the evidence a bundled module supplies: handover, cell retention, and the light-load behavior below. |
| Power-bank controller boards, IP5306 class | Cheapest, and satisfy the electrical contract on paper. Their controllers switch the output off below roughly 45 to 50 mA, which collides with the board's twenty-minute idle sleep unless disabled and proven to stay disabled. |

The survey behind this table, including cell formats and why a 1S pouch wins here despite costing
more per watt-hour than cylindrical cells, is in
[the wiki](../../Vault/Scacchiera/Wiki/synthesis/battery-format-and-module-alternatives.md).

## Cell

The filed Molicel INR-21700-M65A remains a cell candidate, not a bound component: 23.4 Wh typical,
26 A continuous discharge, and a conservative 21.7 by 71.0 mm envelope. It lies lengthwise in the
rail and easily supports the roughly 4 A electrical load. NKON listed the exact flat-top cell as out
of stock on 2026-07-30, while Akkuparts24 offered only a September 2026 preorder. Availability
therefore blocks selection even before pack qualification.

The filed one-page manufacturer sheet and Molicel's product page disagree on height, 71.0 against
70.2 mm, so mechanical work uses the larger value. A newer public but tentative approval sheet
adds detailed pack rules, but the distributor blocks downloading it into the immutable vault and
several of its own performance and regulatory fields remain TBD or estimated. It is useful
reconnaissance, not V1 evidence.

The cell is bare. A qualified assembly must bind welded tabs, insulation, thermistor, lead wire,
connector, transport evidence, and a cell-bonded protection circuit that independently disconnects
both charge and discharge for overtemperature. It must also cut off overcharge, overdischarge,
charge overcurrent, discharge overcurrent, and short circuit. The existing hub interlock remains a
separate, tighter charging safeguard and cannot substitute for pack protection because it has no
authority over discharge.

ABLIC's S-82D1A family demonstrates that a 1-cell protector can combine an external NTC with
separate temperature, voltage, overcurrent, and short-circuit decisions. It is only an architecture
candidate. No exact suffix, supplier code, FET pair, sense resistor, NTC, protection PCB, or pack
assembler is bound, so no new battery board has been added to the inventory.

[Eltec](https://www.elteconline.com/en/about-us/) in Italy and
[ANV Production](https://anvproduction.pl/en/battery-packs/) in Poland are current quote candidates
because they advertise custom pack work, and ANV explicitly advertises prototypes and
small-to-medium runs. Neither has been contacted or selected. A quote is useful only if it returns
the exact cell, protector, temperature and electrical thresholds, construction drawing, connector
and wire details, test record, and transport evidence rather than only a capacity and price.

## Charging

Charging remains moderate. `POWER-CHARGE-10-80` allows 240 minutes and `POWER-CHARGE-10-FULL`
360 minutes. At the fitted 1.5 A target, 70 percent of the 6.5 Ah candidate is 4.55 Ah, or 182 ideal
minutes of constant current. Charging 90 percent takes 234 ideal minutes, leaving 126 minutes for
the constant-voltage taper and control transitions before the full-charge limit. V8 measures both.

## V8 measurements

The exact fitted module and its firmware revision must be recorded before testing. V8 measures:

- 10-to-80 and 10-to-full charge time from a compliant 5 V, 2 A source at 20 to 25 degrees Celsius;
- runtime under the representative gameplay profile;
- 5 V continuity and minimum voltage during source insertion and removal;
- that the 5 V output survives twenty minutes of board sleep without switching off;
- input current, output voltage, and cell-surface temperature while idle and under load;
- reversed-cell insertion with USB absent and already present, plus pass-FET drop and temperature;
- independent charge inhibition below 0 degrees Celsius and at or above 40 degrees Celsius;
- enclosure ventilation, connector strain relief, and NFC performance with the module installed.

A transport test report for the cell is transport evidence only. It is not completed-product
certification and does not waive any V8 or V9 check.

## Mechanical

The module and cell mount in a serviceable rail volume outside the NFC sensing area, with strain
relief, impact protection, no cell compression, and access for replacement. Lithium cells in an
enclosed 3D-printed case need ventilation regardless of which module is fitted, so that is a safety
requirement rather than a cosmetic one.
