# Test article: bare quad boards

A documented test-article release for the sensing plane as **bare copper, unpopulated**. This is
the release [simulation-workflow.md](../simulation-workflow.md) calls a "copper antenna sample" and
recommends over a complete assembled set, and it is the smallest article that can settle the
measurements V4 cannot take from datasheets.

It authorises one thing: fabricating bare quad PCBs for measurement. It does not authorise
assembly, does not authorise any other board, and is not a production release.

It replaces an earlier release of the same shape against the superseded 300 x 300 mm
[matrix board](matrix.md). Same purpose, same measurements, cheaper article, and one of that
article's three pre-upload questions disappears with the board.

## What to order

| Item | Value |
| --- | --- |
| Board | quad (sensing), four lanes |
| Outline | 300.0 x 140.0 mm |
| Quantity | **5** (JLCPCB minimum; a complete plane is four) |
| Layers | 2 |
| Thickness | **0.6 mm** |
| Minimum copper track | 0.200 mm |
| Minimum drill | 0.300 mm |
| Minimum via pad | 0.600 mm |
| Assembly | **none** |
| Artifacts | `hardware/pcb/generated/quad/quad_gerbers.zip` |

The zip carries the complete twelve-file set: both copper layers, both mask, both paste, both
silkscreen, edge cuts, plated and non-plated drills, and the job file. Regenerate with
`make pcb-quad-fab`.

**Five boards is a whole sensing plane plus a spare**, which the matrix article could not offer:
there, five was the minimum and four of them were waste. So this article measures the real
two-plane geometry, row against column, rather than one board's lanes in isolation.

## What is deliberately not in this order

No BOM, no CPL, no assembly. The quad is hand populated anyway
([jlcpcb-sourcing.md](jlcpcb-sourcing.md)), so bare copper is not a compromise. It is also what the
measurements need: an unpopulated antenna is the clean case for a VNA, and the switch cells can be
fitted afterwards to measure their effect separately.

The four harnesses are not in this order either, and for the same reason: they are purchased
accessories, and an unpopulated board has nothing to connect them to. Buy them with the parts, not
with the copper.

## What it is for

Four things, all of which are currently assumptions rather than evidence:

- **A8 and A9** in [assumptions.md](assumptions.md). Avery Dennison publishes no coil inductance,
  turn count or resonant frequency for any converted inlay, and NXP publishes no equivalent
  parallel resistance at minimum operating power. The tag resonator is back-solved. No amount of
  further simulation fixes that; only a measurement does.
- **Antenna complex impedance and Q**, per line, on a calibrated VNA. The design's 0.59 uH comes
  from Grover's formula on the routed geometry, which is an analytical cross-check and, in V4's own
  words, "not release evidence by itself".
- **Coupling and crosstalk with the real SLIX2 tags** across the mechanical tolerance range,
  including the 18 mm coil against a 276 mm line and the read budget through the stack.
- **Whether one line rejects a tag over its neighbour**, which is the assumption the whole
  row-and-column architecture rests on and which the prior art supports but this copper has never
  demonstrated.

Feeding those back into the model is exactly what V4 needs to stop being bounded and start being
sourced, and what V8 requires before any final-board release.

Two measurements this article adds, which the monolith could not have produced at all:

- **`INTERPLANE_GAP` as a real parameter.** On one substrate the row-to-column separation is the
  board thickness. Here it is a printed rib, so the article can be measured at more than one
  separation and the coupling-against-read-budget trade in [quad.md](quad.md) becomes measured
  rather than argued.
- **The butt joint between two boards.** Two 140 mm boards span the 280 mm play area, and whether
  the pitch across that seam is right is a mechanical question no simulation here has answered.

## Before uploading

One thing this project cannot answer from its own files:

- **Copper weight is not specified in the board file.** KiCad defaults apply because no explicit
  stackup block exists, so 1 oz must be chosen in the order.

**Surface finish is settled and it is OSP.** HASL is not offered at 0.6 mm, which forces a choice
between OSP and ENIG, and for this board OSP is right on the merits rather than on price. ENIG's
3 to 6 um nickel underplate has about forty times copper's resistivity and is magnetic, and at
13.56 MHz the skin depth in it is about 3.6 um, comparable to the layer thickness. A real fraction
of the antenna current would flow in that lossy layer. **This article exists to measure loop Q, so
plating the loops in something that degrades Q would corrupt the measurement it is for.**

OSP's shelf life is the trade, and it is acceptable here because the loop terminals are through-hole
pads that get a soldered pigtail rather than a probe on a coated pad. Store the boards dry and
populate them within months rather than years.

**0.6 mm is settled.** Priced 2026-08-02 against 0.8 and 1.0 mm at the same outline and quantity:
all three cost the same, so the thickness the design wants is free and available. This was the last
open fabrication risk on the board.

The matrix article's third question is gone rather than answered: **this board's smallest via is
0.3 mm into a 0.6 mm pad**, the same standard tier as the hub, the lightbar and the power board,
where the matrix used 0.2 into 0.4 and risked falling into a priced-up tier on the largest and most
expensive board in the product. The repartition removed that exposure as a side effect.

Quantity against cost is likewise no longer a question worth a heading: five boards is 20.92 EUR
and is exactly what the measurements need.

## Gate position

Honest statement of what stands behind this release, because
[simulation-workflow.md](../simulation-workflow.md) treats an assumed critical value as a V1
failure and every waiver here is deliberate.

| Gate | State for this article |
| --- | --- |
| V0 | passed |
| V1 | closed on the assumptions in [assumptions.md](assumptions.md) |
| V2 | passed: zero DRC, unconnected and parity findings on this board |
| V3 | not applicable to bare copper, and incomplete generally |
| V4 | **partly extracted**, and this article exists to finish it |
| V5 | firmware not required to fabricate bare copper |
| V6 | not required for this article |
| V7 | **open**: artifacts generated, geometry checked, thickness and finish settled, but no rendered review package and no recorded manufacturer DFM pass |

A bare unpopulated board carries none of the electrical risk V3 covers and none of the assembly
risk V7's BOM and CPL bullets cover, which is why a scoped article is the right shape of release
here while a populated one is not.

**This article is not released.** [planning.md](../planning.md) carries the open V3, V4 and V7
items, and the workflow requires V0 through V7 before any test-article order. What this file
authorises is the *content* of that order once the gate passes, not the order itself.
