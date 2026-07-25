---
type: source-summary
tags:
  - wiki/source
date_updated: 2026-07-25
source_file: "Datasheets/BAR64-02V_C5295579.pdf, Datasheets/BSS123_C7420338.pdf, Datasheets/BSS84_C114481.pdf, Datasheets/74HC595D-118_C5947.pdf, Datasheets/SDFL2012S100KTF_C1046.pdf"
source_title: "Matrix switch-cell discretes: five manufacturer datasheets"
publisher: JSCJ, ICHJC, Jiangsu Changjiang, Nexperia, Sunlord
---

# Matrix switch-cell discrete datasheets

The five parts the [matrix board](../../../../docs/hardware/matrix.md)'s ngspice model rests on.
Filed to close the V1 gap in [simulation-workflow](../../../../docs/simulation-workflow.md): before
this, the switch cell's RF behaviour was simulated from numbers with no filed source.

## BAR64-02V PIN diode, the one that matters most

JSCJ document (jscj-elec.com), the maker LCSC lists for C5295579. SOD-523, 150 V VR.

**There is no single "Rs".** The datasheet gives three forward-resistance maxima, all at 100 MHz:

| Condition | rD max |
| --- | --- |
| IF = 0.5 mA | 9 ohm |
| IF = 1 mA | 6.5 ohm |
| **IF = 10 mA** | **2.5 ohm** |

[rd_max_ohm_at_10ma::2.5] [rd_max_ohm_at_1ma::6.5] [rd_max_ohm_at_0p5ma::9]

This **confirms the existing model**. `hardware/sim/models/bar64_02v.lib` states it "reaches the
stated 2.5 ohm maximum at 10 mA and 100 MHz", which now has a filed source behind it, and the cell's
simulated 10.29 mA bias sits at exactly that operating point. The model's junction-capacitance curve
through 0.55 pF at 1 V and 0.35 pF at 5 V likewise tracks the datasheet maxima.

No carrier lifetime is specified anywhere in the document, which is why the model sets `TT=0` and
declares itself invalid for reverse-recovery transients. That remains a stated limitation, not a
silent assumption.

## SDFL2012S100KTF 10 uH choke, an open margin question

Sunlord SDFL series. **The datasheet gives one current number: Max. Rated Current 15 mA.** There is
no separate saturation-current figure, and the text never says whether 15 mA is a self-heating or an
inductance-drop limit. The only hint is an uncaptioned inductance-versus-DC-current graph, whose
shape suggests a saturation-style limit.

The design pushes the simulated **10.29 mA** bias through it, which is **69% of the only rating
given**. That is thin for a part whose limit type is unknown, and it is now a recorded V3 question
rather than an assumption: sweep it, or pick a choke that publishes a saturation current.

[rated_current_ma::15] [design_bias_ma::10.29] [margin_fraction::0.69]

## MOSFETs

BSS123 (N-channel) and BSS84 (P-channel), the shunt and the bias steer. Threshold, Rds(on), and
Ciss/Coss/Crss with their test conditions are transcribed in full in the working notes. The
capacitances are what set the deselected cell's loading on the shared bus, so they feed
`bss123.lib` and `bss84.lib`.

## 74HC595 shift register

Nexperia. **The electrical table has no 3.3 V or 5 V rows**: it specifies at 2 V, 4.5 V and 6 V
only. The bracketing values are recorded rather than interpolated, because interpolating a
propagation delay and calling it a datasheet value is exactly what the Datasheets rule forbids. OE
and MR are recorded with their active levels.

## Maker ambiguities, recorded not resolved

LCSC's brand tags do not match the documents it serves, for two of these:

- **BSS123 (C7420338)**: LCSC tags the brand "R+O", and the datasheet it serves is letterheaded
  **Zhuhai Hongjiacheng / ICHJC**. Neither is JSCJ.
- **BSS84 (C114481)**: LCSC tags "JSCJ", but the document is from **Jiangsu Changjiang Electronics**
  (cj-elec.com), a different company from the BAR64's Jiangsu Changjing (jscj-elec.com) despite the
  near-identical name.
- **SDFL2012S100KTF (C1046)**: LCSC's own datasheet link failed, and a JLCPCB CDN link served a
  JLCPCB ISO-27001 certificate mis-tagged under C1046. The filed document is the Sunlord SDFL-series
  sheet from a Digikey mirror.

In each case the filed document is the one the vendor actually serves for that order code. Per the
Datasheets rule, conflicting documentation is recorded, and under
[simulation-workflow](../../../../docs/simulation-workflow.md) V1 a conflict blocks release until
resolved.

Related: [[pin-diode-antenna-switching]], [[row-column-antenna-matrix-technique]], [[jlcpcb]]
