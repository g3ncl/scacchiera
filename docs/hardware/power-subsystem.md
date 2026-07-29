# Power subsystem selection

Which purchased module and cell fill the boundary defined in
[power-module-interface.md](power-module-interface.md). That file is the contract; this one records
what is fitted, what was considered, and what still has to be measured.

## Status

**No module is bound.** The interface is deliberately written as a contract rather than around one
product, so the board can be built and verified before the choice is final, and the module can be
swapped later without touching the hub.

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

Any cell meeting the runtime requirement and the 46 mm width. The reference point is an 18.5 Wh
1S pouch, around 10 mm thick and 100 to 120 mm long, since rail length is the dimension this
enclosure has to spare. The cell carries its own protection board; the hub adds the cell-bonded
thermistor and the analog window, because pouch cells of this class ship without an NTC.

## Charging

Charging is deliberately slow. `POWER-CHARGE-10-80` allows 240 minutes and `POWER-CHARGE-10-FULL`
360 minutes, which a 1 A charger meets: 70 percent of a 5 Ah cell is 3.5 Ah, or 210 minutes of
constant current. This is what admits the cheap module tier, and it is a deliberate trade of
recharge speed for subsystem cost. The constant-voltage taper does not scale down with current,
which is why the full-charge limit is not simply double.

## V8 measurements

The exact fitted module and its firmware revision must be recorded before testing. V8 measures:

- 10-to-80 and 10-to-full charge time from a compliant 5 V, 2 A source at 20 to 25 degrees Celsius;
- runtime under the representative gameplay profile;
- 5 V continuity and minimum voltage during source insertion and removal;
- that the 5 V output survives twenty minutes of board sleep without switching off;
- input current, output voltage, and cell-surface temperature while idle and under load;
- independent charge inhibition below 0 degrees Celsius and at or above 40 degrees Celsius;
- enclosure ventilation, connector strain relief, and NFC performance with the module installed.

A transport test report for the cell is transport evidence only. It is not completed-product
certification and does not waive any V8 or V9 check.

## Mechanical

The module and cell mount in a serviceable rail volume outside the NFC sensing area, with strain
relief, impact protection, no cell compression, and access for replacement. Lithium cells in an
enclosed 3D-printed case need ventilation regardless of which module is fitted, so that is a safety
requirement rather than a cosmetic one.
