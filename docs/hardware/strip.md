# Split sensing plane: line strips and spines

An alternative to the monolithic [matrix board](matrix.md), carrying the same sixteen line
antennas on sixteen identical 300 x 33 mm strips stacked crosswise in two planes, cabled to two
290 x 28 mm spine boards. Schematics in `hardware/pcb/strip.py` and `hardware/pcb/spine.py`,
geometry in `hardware/pcb/strip_geometry.py`, layouts in `hardware/pcb/strip_layout.py` and
`hardware/pcb/spine_layout.py`.

This is a partition, not a redesign. Every loop keeps its dimensions and its position in the play
area, every switch cell is the same `matrix_cell` the matrix board instantiates sixteen times, and
selection is the same pair of chained 74HC595s driving the same one-hot active-low lines. What
moves is where the board boundary falls.

## Why the boundary falls where it does

An earlier split was considered and rejected in [jlcpcb-sourcing.md](jlcpcb-sourcing.md): a dumb
antenna board plus a small switch daughterboard. That one put connector inductance inside all
sixteen resonant tanks, between each loop and its 220 pF, which nothing could compensate.

This partition cuts elsewhere. A strip carries its loop **and** its whole tank: the 220 pF, both
DNP trim pads, the series PIN diode, the shunt FET and the 100 nF DC block. The connector sits on
the far side of that DC block. So the harness is series impedance on the **shared bus**, which is a
tunable, measurable, second-order effect, rather than a term inside sixteen resonators.

`hardware/tests/test_strip.py::test_the_tank_never_crosses_the_connector` holds that boundary: it
asserts no tank net reaches J1.

## What it costs, measured

Every figure below comes from a test in the suite, against a limit in
[criteria.yaml](criteria.yaml).

| | monolith | split | source |
| --- | ---: | ---: | --- |
| Loop self inductance | 566.6 nH | 566.6 nH | `hardware/sim/strip_stack.py` |
| Adjacent-line coupling | 0.1401 | 0.1401 | same |
| Worst row-to-column coupling | 0.0664 | **0.0652** | same |
| Plane separation | 0.965 mm | 1.035 mm | `hardware/pcb/strip_geometry.py` |
| Bus resonance, all sixteen lines | 12.895 MHz | 12.836 to 12.875 MHz | `hardware/sim/strip_rf.py` |
| Line-to-line resonance spread | 0 | **0.31 percent** | same |
| Series interconnect per line | 0 | 142 to 385 nH | same |
| Fitted parts | 4.80 EUR | **15.16 EUR** | generated BOMs |
| Placed references | 165 | **200** | generated BOMs |
| Substrate area | 90,000 mm2 | **174,640 mm2** | `test_strip.py` |
| Large-size assembly charge | 50.47 EUR | **0.00 EUR** | 2026-08-02 quote |
| One working plane, bare | 58.34 EUR | **26.92 EUR** | 2026-08-02 quote |
| One working plane, assembled | 141.05 EUR | **101.12 EUR** | 2026-08-02 quote |

The electrical cost is small, the bill-of-materials cost is real, and the fabrication cost turned
out to favour the split in both build regimes. See [jlcpcb-sourcing.md](jlcpcb-sourcing.md) for the
quote and its caveats.

The area penalty is genuine and unchanged: 1.94 times the substrate, structural rather than a
layout inefficiency, because the monolith carries two antenna planes on one substrate's two faces
and any per-line strip uses one face and wastes the other. What outweighs it is that a 300 by 33 mm
outline pays no large-size assembly charge where a 300 by 300 mm one pays 50.47 EUR, and that
JLCPCB's five-piece minimum forces four unusable matrix boards where twenty strips is a set plus
spares.

### The interconnect barely detunes anything

`hardware/sim/strip_rf.py` runs the same sixteen cells twice through one testbench, once with the
harness and spine path and once with them removed, so the difference between the two numbers is
the interconnect and nothing else. The whole path costs **0.46 percent** of tuning.

That is the structural argument made numeric. A tank behind a series inductor is not a tank with an
inductor in it: at parallel resonance the tank is a high impedance, and putting 385 nH in front of
a high impedance barely moves where the peak sits. The 100 nF DC block is what puts the connector
outside rather than inside.

### The spread is the number that had to be earned

The harness is common to all sixteen lines **by construction**, because
`strip_geometry.HARNESS_LENGTH_MM` makes every harness the same length. A common term detunes all
sixteen together and the nominal 220 pF absorbs it. Equal lengths matter more than short ones here,
and that is why the constant exists.

The spine path is not common. Line 0 taps the bus beside the feed and line 15 taps it two spines
away, so the sixteen lines cannot all be corrected by one capacitor value. That spread is
**0.31 percent** worst case against a 2 percent limit, comfortably inside what the DNP trim pads
already on every strip can take out.

### The connector assumption does not decide anything

Contact inductance is **A11** in [assumptions.md](assumptions.md): JST publishes none for the GH
series and no connector vendor at this price does. Rather than pick a number, the deck sweeps 2 to
8 nH per mated pair, a fourfold range, and the band moves by less than one sweep step. Nothing in
the split rests on the assumption, which is what lets it proceed with A11 open.

## Stackup

Two substrates now sit where one used to. Both loops are on their strip's **top** copper, so the
near plane is at the top of the assembly exactly as the monolith's front-copper rows were.

```
                 pieces
   -------------------------------------  column strip top copper   z = 1.035
   [ 0.6 mm substrate ]
   ---- 0.4 mm frame rib (INTERPLANE_GAP) ----
   -------------------------------------  row strip top copper      z = 0.000
   [ 0.6 mm substrate ]
```

`INTERPLANE_GAP` is the knob the monolith did not have: on one substrate the plane separation is
whatever the board thickness is, and here it is independent of it, in both directions. It is set to
reproduce the monolith at 1.035 mm against 0.965 mm rather than to exploit that freedom, and
deliberately so. Moving it would have changed every coupling figure in
[criteria.yaml](criteria.yaml) at the same time as changing the board, which makes neither change
reviewable.

The direction of the trade, if it is ever wanted: closing the gap improves the read budget and
worsens row-to-column coupling, which is already 3.9 times the nfcgameboard prior art. Opening it
does the reverse. The far plane currently sits 0.07 mm deeper than the monolith's, 2 percent of the
3.0 mm budget in [functional/physical.md](../functional/physical.md).

## The strip

300 x 33 mm, 2 layers, **0.6 mm**. 33 inside the 35 mm lane leaves 0.5 mm of copper-to-edge either
side of the 31 mm loop and a 2.0 mm air gap between neighbouring strips for the frame's rib.

The loop is front copper and every component is on the back, which is the monolith's rule and the
reason it exists: the top face stays flat against the controlled air gap. Nothing but antenna
copper goes past 14.5 mm, enforced with a keepout rather than left to the router, so the 276 mm of
loop can never acquire a signal track crossing it.

The twelve cell parts sit in two columns of six in that 12.5 mm zone, ordered along the signal
chain so every net joins parts that are physically adjacent. Six consecutive parts share the match
node, which is why they are one column.

**No mounting hole, deliberately.** The printed frame captures each strip in a channel along its
full 300 mm, so a screw adds nothing the channel does not. There is also nowhere to put one: the
loop spans the strip's whole width for 276 of those 300 mm, the connector end is committed, and a
grounded 5.4 mm pad at the far end would sit 3.2 mm from the loop and load it. Retention is a
print-iteration matter, which V7 moved out of the gate precisely because a reprint fixes it and a
respin does not.

## The spine

290 x 28 mm, 2 layers, 1.0 mm. One design built twice, one under each plane's connector ends.

Four bands across the width: eight strip sockets on the 35 mm lane pitch facing the strips, the
shared RF bus behind them as a 3 mm microstrip over solid back-copper ground, a clear channel, then
the 74HC595 and its decoupling. The bus is drawn by the layout rather than handed to Freerouting,
because its inductance is the one thing the split adds that the monolith did not have, and it has
to come from a geometry the simulation can read back.

The pair chains exactly as U1 and U2 did on the monolith: hub into the first spine's link in, its
QH' out on the link out, that into the second spine's link in. Both links carry the same seven
conductors, so one pinout serves both directions.

The upper eight lines therefore reach the bus through the whole of the first spine plus the
spine-to-spine link, which is why lines 8 to 15 carry roughly twice the series inductance of lines
0 to 7. That asymmetry is recorded rather than hidden: two identical boards do not mean two
identical bus paths, and `test_sim_strip.py::test_the_upper_bank_pays_for_the_daisy_chain` fails if
it ever stops being true.

### The registers still cannot be cleared

`SRCLR_N` is tied to 3V3 and `OE_N` to ground, the same permanently-enabled arrangement
[matrix.md](matrix.md) documents. The split does not fix it and cannot: the seven-conductor hub
link has no spare conductor, and the hub does not route the net to its connector in the first
place. Shifting a known sixteen-bit pattern stays the driver's mandatory first action, and
`hardware/pcb/firmware_pins.py` still keeps the dead net out of the generated header.

## Interconnect

Eighteen JST GH cable assemblies: sixteen strip harnesses at
`strip_geometry.HARNESS_LENGTH_MM` and two link harnesses. They are purchased accessories on no
board BOM, like the hub's antenna pigtail, and an order that forgets them is incomplete.

**The split introduces no new component type.** The strip's connector is the same
SM07B-GHS-TB the matrix board already binds, seven conductors and all, rather than a narrower
five-pin part. Two spare pins are cheaper than a new unique Extended selection, which would cost a
2.70 EUR feeder change and a datasheet ingest; the spares go to ground, so the RF conductor runs
between grounds at both ends of the housing.
`test_strip.py::test_the_split_introduces_no_new_component_type` holds that.

Thirty-six connectors at 0.296 EUR is 10.66 EUR, and the split's entire 10.36 EUR parts increase
over the monolith is that and nothing else. Modularity is what is being bought, and this is the
price.

## What is not settled

- **The thickness the strip actually needs.** The 2026-08-02 quote priced all three boards at
  JLCPCB's default 1.6 mm, where the strip is designed at 0.6. Two-layer boards are usually the
  same price across that range, so the result is expected to hold, but a 0.6 mm board 300 mm long
  is the one parameter still unpriced. If it is refused or surcharged, the fallback is 1.0 mm
  strips with `INTERPLANE_GAP` cut to 0.0, which holds the 1.035 mm separation but makes the frame
  guarantee the gap mechanically instead of with a rib.
- **The frame.** Sixteen strips at a 35 mm pitch across 280 mm, held coplanar, with the column
  plane on 0.4 mm ribs above the rows. That is print-iteration work and owner-managed per V7, but
  nothing in this repository has drawn it.
- **Everything V8 already had to measure.** The split changes none of it. Coupling remains a
  recorded ceiling rather than a demonstration of adequacy, and A8 and A9 still stand.
