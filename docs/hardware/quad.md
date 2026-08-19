# Split sensing plane: four-lane boards

An alternative to the monolithic [matrix board](matrix.md), carrying the same sixteen line
antennas on four identical 300 x 140 mm boards stacked crosswise in two planes. Schematic in
`hardware/pcb/quad.py`, geometry in `hardware/pcb/quad_geometry.py`, layout in
`hardware/pcb/quad_layout.py`.

This is a partition, not a redesign. Every loop keeps its dimensions and its position in the play
area, every switch cell is the same `matrix_cell` the matrix board instantiates sixteen times, and
selection is the same 74HC595 driving the same one-hot active-low lines. What moves is where the
board boundary falls.

## Why four

Four is where the cost curve turns, and it was measured rather than chosen.

One board per line was designed first and rejected on its own numbers: sixteen strips plus two
spine boards need **thirty-six connectors and eighteen harnesses**, and that alone was the entire
10.36 EUR parts increase over the monolith. Four lanes per board collapses it to eight connectors
and four harnesses, deletes the spine design outright, and costs nothing electrically that matters.

Eight lanes per board would be 280 mm wide, back inside the size charges this partition exists to
escape. Four boards is also exactly one set against a five-piece minimum order, so a set arrives
with one spare rather than four wasted.

| | matrix | 16 strips + 2 spines | **4 quads** |
| --- | ---: | ---: | ---: |
| Designs | 1 | 2 | **1** |
| Boards per set | 1 | 18 | **4** |
| Connectors | 1 | 36 | **8** |
| Harnesses | 1 | 18 | **4** |
| Parts cost per set | 4.80 EUR | 15.16 EUR | **7.28 EUR** |
| Bare PCB, one set | 58.34 EUR | 26.92 EUR | **20.92 EUR** |
| Substrate | 90,000 mm2 | 158,400 mm2 | 168,000 mm2 |

## Why the boundary falls where it does

An earlier split was considered and rejected in [jlcpcb-sourcing.md](jlcpcb-sourcing.md): a dumb
antenna board plus a small switch daughterboard. That one put connector inductance inside all
sixteen resonant tanks, between each loop and its 220 pF, which nothing could compensate.

This partition cuts elsewhere. Each lane carries its loop **and** its whole tank: the 220 pF, both
DNP trim pads, the series PIN diode, the shunt FET and the 100 nF DC block. The connectors sit on
the far side of that DC block. So a harness is series impedance on the **shared bus**, which is a
tunable, measurable, second-order effect, rather than a term inside sixteen resonators.

`hardware/tests/test_quad.py::test_the_tank_never_crosses_a_connector` holds that boundary.

## What it costs, measured

| | monolith | split | source |
| --- | ---: | ---: | --- |
| Loop self inductance | 566.5 nH | unchanged | `hardware/sim/quad_stack.py`, pinned equal within 0.2 percent |
| Adjacent-line coupling | 0.1401 | 0.1401 | same, re-extracted 2026-08-19, both 0.14007 |
| Worst row-to-column coupling | 0.0664 | **0.0652** | same |
| Plane separation | 0.965 mm | 1.035 mm | `hardware/pcb/quad_geometry.py` |
| Bus resonance, all sixteen lines | 12.895 MHz | 12.767 to 12.865 MHz | `hardware/sim/quad_rf.py` |
| Line-to-line resonance spread | 0 | **0.77 percent** | same |
| Series interconnect per line | 0 | 181 to 773 nH | same |
| Large-size assembly charge | 50.47 EUR | **0.00 EUR** | quoted for the monolith, inferred for the split |
| Placed references per set | 165 | 176 | generated BOM |
| Substrate area | 90,000 mm2 | **168,000 mm2** | `test_quad.py` |

**The adjacent-coupling conflict is resolved.** Both extractions were re-run on 2026-08-19 and
both return k = 0.14007: the split's recorded 0.1401 was correct and the monolith's 0.1398 was a
stale transcription, now corrected in [criteria.yaml](criteria.yaml). The pinning test
`test_quad_stack.py::test_adjacent_lines_are_no_worse_than_the_monolith` was right all along: the
in-plane geometry is untouched.

The RF numbers are unchanged or better, and the fabrication cost favours the split. The substrate
penalty is real and structural: the monolith carries two antenna planes on one substrate's two
faces, and any per-lane split uses one face and wastes the other. What outweighs it is that a
300 by 140 mm outline pays no size charge where a 300 by 300 mm one pays 50.47 EUR.

### The interconnect barely detunes anything

`hardware/sim/quad_rf.py` runs the same sixteen cells twice through one testbench, once with the
harness-and-chain path and once with it removed, so the difference between the two numbers is the
interconnect and nothing else. The whole path costs at most **0.99 percent** of tuning.

That is the structural argument made numeric. A tank behind a series inductor is not a tank with an
inductor in it: at parallel resonance the tank is a high impedance, and putting 773 nH in front of
a high impedance barely moves where the peak sits. The 100 nF DC block is what puts the connectors
outside rather than inside.

**Every figure there is a bound, not a nominal.** The on-board bus is autorouted, so each line is
modelled at the whole net's routed length, which no single tap-to-tap path can exceed. That gives
all four lanes of a board the same series inductance and overstates three of them.
`test_sim_quad.py` re-measures the routed copper and fails if the bound stops bounding it.

### The spread is the number that had to be earned

Each harness is the same length **by construction** (`quad_geometry.HARNESS_LENGTH_MM`), so a
board's four lanes are detuned together and the nominal 220 pF absorbs it.

What is not common is a board's place in the chain: the first taps the bus one harness from the
reader, the fourth four harnesses and three boards away. That spread is **0.77 percent** worst case
against a 2 percent limit, inside what the DNP trim pads already on every lane can take out. It is
worse than the sixteen-strip layout's 0.31 percent, and that is the price of chaining four boards
instead of two spines.

### The connector assumption does not decide anything

Contact inductance is **A11** in [assumptions.md](assumptions.md): JST publishes none for the GH
series. Rather than pick a number, the deck sweeps 2 to 8 nH per mated pair, a fourfold range, and
the band moves by one sweep step.

## Stackup

Both loops sit on their board's **top** copper, so the near plane is at the top of the assembly
exactly as the monolith's front-copper rows were.

```
                 pieces
   -------------------------------------  column board top copper   z = 1.035
   [ 0.6 mm substrate ]
   ---- 0.4 mm frame rib (INTERPLANE_GAP) ----
   -------------------------------------  row board top copper      z = 0.000
   [ 0.6 mm substrate ]
```

`INTERPLANE_GAP` is the knob the monolith did not have: on one substrate the plane separation is
whatever the board thickness is, and here it is independent of it, in both directions. It is set to
reproduce the monolith at 1.035 mm against 0.965 mm rather than to exploit that freedom, and
deliberately so. Moving it would have changed every coupling figure in
[criteria.yaml](criteria.yaml) at the same time as changing the board.

**0.6 mm on a 300 mm outline is confirmed and costs nothing extra.** Priced 2026-08-02 against 0.8
and 1.0 mm at the same outline and quantity: all three are the same price, so the stock the design
wants is free. This was the last open fabrication risk on the board and it is now closed.

It does carry one consequence worth stating here rather than only in the order: **HASL is not
offered at 0.6 mm**, so the finish is OSP or ENIG. This board takes **OSP**, and on RF grounds
rather than cost. ENIG's nickel underplate is roughly forty times copper's resistivity and magnetic,
and at 13.56 MHz the skin depth in it is comparable to its own thickness, so antenna current would
partly run in the lossy layer and spend loop Q. See [ordering.md](ordering.md).

Worth knowing that an earlier revision claimed this thickness was "quoted and accepted" on the
strength of a quote taken at JLCPCB's default 1.6 mm. That claim was withdrawn as unverified before
the thickness was actually priced, so the conclusion is the same but the evidence behind it is not.

The escape route this made unnecessary is worth keeping in mind, because it is the freedom the split
bought: row-to-column separation is `QUAD_THICKNESS + INTERPLANE_GAP`, so if thin stock had priced
badly, 0.8 mm board with a 0.2 mm rib would give the identical 1.0 mm separation.

## The board

300 x 140 mm, 2 layers, 0.6 mm, four lanes on the 35 mm play pitch. Two boards butt together to
span the 280 mm play area with no cumulative pitch error between them, and the same board rotated a
quarter turn is the column plane.

The loops are front copper and every component is on the back, which is the monolith's rule and the
reason it exists: the top face stays flat against the controlled air gap. Nothing but antenna
copper goes past 14.5 mm, enforced with a keepout rather than left to the router, so the four
276 mm loops can never acquire a track crossing them.

Fifty-two footprints live in that 14.5 by 140 mm zone. Four lane clusters of twelve sit on the lane
centres in two columns of six, ordered along the signal chain so every net joins parts that are
physically adjacent; the three things too wide for a cluster (both links and the register) go in
the gaps between lanes. The 3.6 mm cell row pitch exists to protect those gaps: at 4.0 mm they
closed to 11.5 mm and a rotated GH housing, 11.2 mm across its mounting pads, no longer cleared its
neighbours.

**No chin.** The component zone is inside the 300 mm envelope, not added to it. It is the same
15 mm the play area was already offset by, and the matrix board spends that margin on components
too, so the split adds no protrusion the monolith does not already have.

**No mounting hole, deliberately.** The printed frame captures each board in a channel along its
full 300 mm. There is also nowhere to put one: the loops span the board's whole width for 276 of
those 300 mm, and the connector end is committed.

## Selection

One 74HC595 per board with four of its eight outputs used. The waste is deliberate and cheap, a
Basic part at 0.20 EUR; the alternative is eight lanes per board and a 280 mm outline.

The four boards chain exactly as the matrix board's U1 and U2 did: the hub drives the first link
in, its QH' leaves on the link out, the next board takes that as its serial in. Both links carry
the same seven conductors, so one pinout serves both directions and **the hub interface is
unchanged**.

**It does cost a firmware change, and it is done.** The chain is four registers deep, so a scan
shifts 32 bits with the one-hot bit in the low nibble of each, where the matrix board shifts 16.
That was the one thing this partition asked of software.
`software/firmware/port/matrix_encoding.h` implements it and
`software/firmware/test/test_matrix_encoding.c` pins it.

The subtlety worth stating, because it is where a plausible implementation goes wrong: **the
line-to-bit map is not linear.** A board uses QA to QD and leaves QE to QH open, so line n lands on
bit `8 * (n / 4) + (n % 4)`, not bit n. A stride of 4 would alias two boards onto each other and
would look correct on any single board. The mapping also fixes an assembly convention nothing on
the boards themselves records: boards 0 and 1 in chain order are the row plane, 2 and 3 the column
plane, since the four are identical.

### The registers still cannot be cleared

`SRCLR_N` is tied to 3V3 and `OE_N` to ground, the same permanently-enabled arrangement
[matrix.md](matrix.md) documents. The split does not fix it and cannot: the seven-conductor hub
link has no spare conductor, and the hub does not route the net to its connector in the first
place. Shifting a known pattern stays the driver's mandatory first action.

## Interconnect

Four JST GH cable assemblies at `quad_geometry.HARNESS_LENGTH_MM`. They are purchased accessories
on no board BOM, like the hub's antenna pigtail, and an order that forgets them is incomplete.

**The split introduces no new component type.** The links are the same SM07B-GHS-TB the matrix
board already binds, seven conductors and all, rather than a wider part carrying four selects.
Keeping the selection serial is what holds the hub interface fixed and the whole partition at zero
new bound parts. `test_quad.py::test_the_split_introduces_no_new_component_type` holds that.

## What is not settled

- **The frame.** Four boards at a 35 mm lane pitch, held coplanar, with the column plane on 0.4 mm
  ribs above the rows. Far easier than sixteen loose strips, but nothing in this repository has
  drawn it. Print-iteration work, owner-managed per V7. It is also what fixes chain order against
  plane, which the firmware's encoding now assumes.
- **Everything V8 already had to measure.** The split changes none of it. Coupling remains a
  recorded ceiling rather than a demonstration of adequacy, and A8 and A9 still stand.
