# Test article: bare matrix board

A documented test-article release for the sensing board as **bare copper, unpopulated**. This is
the release [simulation-workflow.md](../simulation-workflow.md) calls a "copper antenna sample" and
recommends over a complete assembled set, and it is the smallest article that can settle the
measurements V4 cannot take from datasheets.

It authorises one thing: fabricating bare matrix PCBs for measurement. It does not authorise
assembly, does not authorise any other board, and is not a production release.

## What to order

| Item | Value |
| --- | --- |
| Board | matrix (sensing) |
| Outline | 300.0 x 300.0 mm |
| Layers | 2 |
| Thickness | **1.0 mm** |
| Minimum copper track | 0.200 mm |
| Minimum drill | 0.200 mm |
| Minimum via pad | 0.400 mm |
| Assembly | **none** |
| Artifacts | `hardware/pcb/generated/matrix/matrix_gerbers.zip` |

The zip carries the complete twelve-file set: both copper layers, both mask, both paste, both
silkscreen, edge cuts, plated and non-plated drills, and the job file. Regenerate with
`make pcb-matrix-fab`.

## What is deliberately not in this order

No BOM, no CPL, no assembly. The matrix is hand-populated anyway, because
[jlcpcb-sourcing.md](jlcpcb-sourcing.md) records that its outline is outside the assembly service,
so bare copper is not a compromise for this board. It is also what the measurements need: an
unpopulated antenna is the clean case for a VNA, and the switch cells can be fitted afterwards to
measure their effect separately.

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
  including the 18 mm coil against a 276 mm line and the read budget through the 1.0 mm substrate.
- **Whether one line rejects a tag over its neighbour**, which is the assumption the whole
  row-and-column architecture rests on and which the prior art supports but this copper has never
  demonstrated.

Feeding those back into the model is exactly what V4 needs to stop being bounded and start being
sourced, and what V8 requires before any final-board release.

## Before uploading

Three things this project cannot answer from its own files:

1. **The 0.2 mm via drills into 0.4 mm pads.** Tighter than the 0.3/0.6 the other three boards use,
   and possibly outside a fabricator's standard tier. This is the largest board in the product, so a
   tier change here is the most expensive one to discover late. Confirm against the fabricator's
   current capability page, and if it prices up, the vias are worth revisiting before ordering
   rather than after.
2. **Copper weight and surface finish are not specified in the board file.** KiCad defaults apply
   because no explicit stackup block exists, so both must be chosen in the order. 1 oz and HASL or
   ENIG are the ordinary choices; ENIG is flatter, which matters more for the fine-pitch parts on
   the hub than for this board.
3. **Quantity against cost.** At 300 x 300 mm this is 900 cm2 of board, and fabricators price
   two-layer work by area, so this is the dominant cost in the product and minimum order quantity
   multiplies it. One or two articles are enough for the measurements above.

## Gate position

Honest statement of what stands behind this release, because
[simulation-workflow.md](../simulation-workflow.md) treats an assumed critical value as a V1
failure and every waiver here is deliberate.

| Gate | State for this article |
| --- | --- |
| V0 | passed |
| V1 | closed on the ten assumptions in [assumptions.md](assumptions.md) |
| V2 | passed: zero DRC, unconnected and parity findings on this board |
| V3 | not applicable to bare copper, and incomplete generally |
| V4 | **not started**, and this article exists to make it possible |
| V5 | firmware not required to fabricate bare copper |
| V6 | not required for this article |
| V7 | artifacts generated and geometry checked; no quote, and no enclosure fit because no enclosure model exists |

A bare unpopulated board carries none of the electrical risk V3 covers and none of the assembly
risk V7's BOM and CPL bullets cover, which is why a scoped article is releasable here while a
populated one is not.
