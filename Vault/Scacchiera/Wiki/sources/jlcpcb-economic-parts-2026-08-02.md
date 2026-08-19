---
type: source-summary
date_updated: 2026-08-02
tags:
  - wiki/source
---

# JLCPCB economic parts catalog, 2026-08-02

Raw capture: `Clippings/jlcpcb/economic-parts-2026-08-02.csv`, 771 kB, 2004 rows.
Origin: [lrks/jlcpcb-economic-parts](https://github.com/lrks/jlcpcb-economic-parts), which republishes
JLCPCB's Basic and Preferred Extended lists weekly as CSV at
`https://lrks.github.io/jlcpcb-economic-parts/economic-parts.csv`. Same generator as the
[[jlcpcb-economic-parts-2026-07-24|2026-07-24 capture]], refreshed.

## Why this list and not the full catalog

**Economic parts are exactly the parts that carry no feeder-loading fee.** JLCPCB charges roughly
2.70 EUR per unique Extended component for Economic PCBA, and waives it for both Basic and
**Preferred Extended** parts. So the boundary that matters to this project's cost is not
Basic-versus-everything, it is *in this list or not in this list*.

The full JLCPCB library is 700k+ parts and is not worth mirroring here. This list is 771 kB and
answers the only catalog question the design actually asks.

## Shape of the data

| Field | Meaning |
| --- | --- |
| `code` | LCSC part number, the key the generated BOMs already use |
| `library` | `base` for Basic, `expand` for Preferred Extended. Both are fee-free. |
| `deleted` | `1` if withdrawn since first seen. 418 of 2004 rows are withdrawn. |
| `price`, `stock`, `MOQ` | catalog figures, time-sensitive |
| `pcbaMinQty`, `pcbaMinPrice` | assembly minimum quantity and its price |
| `describe` | the parametric string, which is where the electrical values live |

Live (non-deleted) rows: **1586**, of which **351 Basic** and **1235 Preferred Extended**.

## The finding: this catalog is passives and discretes, almost nothing else

Complete category breakdown of the 1586 live rows:

| Count | Category |
| ---: | --- |
| 591 | Diodes |
| 324 | Circuit Protection |
| 298 | Resistors |
| 138 | Capacitors |
| 131 | Transistors/Thyristors |
| 22 | Power Management (PMIC) |
| 13 | Inductors, Coils, Chokes |
| 10 | Interface |
| 9 | Amplifiers/Comparators |
| 7 | Crystals; 7 Optoelectronics; 7 Memory; 7 Logic |
| 6 | Embedded Processors & Controllers |
| 4 | Filters; 4 Optoisolators; 3 Clock/Timing; 2 Switches; 1 Sensors; 1 LED Drivers; 1 Signal Isolation |

**1482 of 1586 are diodes, protection, resistors, capacitors and transistors.** And two counts
decide this project's open substitution question outright:

- **Connectors: 0.** Not few, none. There is no fee-free connector of any kind.
- **Modules: 0.** No RF or MCU module is ever fee-free.
- Crystals: 7, at 32.768 kHz, 8, 11.0592, 12, 16 and 25 MHz. **None at 27.12 MHz**, the frequency
  PN5180 Table 142 fixes. The two 3225 parts (C13738, C9002) match the footprint exactly and are
  the wrong frequency, which is the near miss worth recording so it is not rediscovered.

## Bearing on the design

Checked directly: **none of the seven feeder-fee parts in this project appear in this list**, in
either the 07-24 or the 08-02 capture. C3020560 (USB-C), C1526287 (PN5180), C7558096 (ESP32-C6
module), C90919 (27.12 MHz crystal), C2865523 (CSD25404Q3), C80200 (BQ25895), C87357 (TPS61088).

The category counts explain why, and turn "we could not find a substitute" into "no substitute of
that class exists in the fee-free catalog". See [[jlcpcb-basic-part-sourcing]] and
[[pcba-cost-structure]].

Conversely every fee-free part the design already selected is confirmed present: C1525 (100 nF
0402), C5947 (74HC595), C25803 (100 k), C1046 (10 uH) all resolve, all `base`.

## Drift against the 2026-07-24 capture

**Membership is identical.** All 2004 rows are the same parts; only `price`, `stock` and `lastSeen`
moved. Nothing entered or left the fee-free catalog in nine days, which is worth knowing before
re-checking a substitution question: the answer is stable on a scale of weeks.

## How to query it

```bash
# Is a given LCSC code fee-free?
grep '^C1525,' Vault/Scacchiera/Clippings/jlcpcb/economic-parts-2026-08-02.csv | cut -d, -f1,4

# Live fee-free parts in a category, with their parametric string
python - <<'PY'
import csv
rows=[r for r in csv.DictReader(open('Vault/Scacchiera/Clippings/jlcpcb/economic-parts-2026-08-02.csv'))
      if r['deleted']=='0' and r['category']=='Capacitors']
for r in rows[:20]: print(r['code'], r['library'], r['model'], r['package'], r['describe'][:60])
PY
```

For interactive parametric search over the **full** catalog, use
[jlcparts](https://yaqwsx.github.io/jlcparts/) rather than this file. This capture is the offline,
dated, greppable record of the fee-free subset.

## Caveats

- Price and stock are time-sensitive and are not release evidence.
- A parametric string is not a datasheet. Per `CLAUDE.md`, any electrical limit still comes from a
  filed datasheet in `Datasheets/`.
- Presence here means fee-free at capture time, not that JLCPCB will place the part on a given
  order; confirm in the live BOM match before payment.

## Related

- [[jlcpcb]]
- [[jlcpcb-basic-part-sourcing]]
- [[pcba-cost-structure]]
- [[jlcpcb-economic-parts-2026-07-24]]
