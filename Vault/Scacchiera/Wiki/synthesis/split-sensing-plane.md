---
type: synthesis
date_updated: 2026-08-02
tags:
  - wiki/synthesis
---

# Where a board boundary can cut a resonant sensing plane

The sensing plane's sixteen line antennas can live on one 300 by 300 mm substrate or on several
smaller ones. Two questions turned out to be hiding in that, and they have different answers:
**where the board boundary is allowed to fall** electrically, and **how many pieces to cut it
into** economically.

The design that came out of this is
[[../../../../docs/hardware/quad.md|docs/hardware/quad.md]], four boards of four lanes; the monolith
it is an alternative to is [[../../../../docs/hardware/matrix.md|docs/hardware/matrix.md]].

## The rule the two splits differ on

A cell is a tank (loop, 220 pF, trim pads, series PIN diode, shunt FET) fed through a 100 nF DC
block from the shared bus. A connector can go on either side of that block, and the two choices are
not comparable.

**Inside the tank.** An antenna board plus a switch daughterboard puts connector inductance between
each loop and its tuning capacitor, so it joins sixteen resonators. It changes what they resonate
at, per unit, with no compensation available. This is the split
[[../../../../docs/hardware/jlcpcb-sourcing.md|jlcpcb-sourcing.md]] rejected, correctly. See also
[[pin-diode-antenna-switching]] for why the series element is a PIN diode in the first place.

**Outside the tank.** A board carrying whole tanks puts the connector on the bus side of the DC
block, so the harness is series impedance between the reader and a *parallel*-resonant branch. At resonance that branch is a high impedance, and adding series reactance in front of a
high impedance barely moves where the peak sits.

The measured difference: 142 to 385 nH of harness and spine, depending on line and corner, moves
the bus resonance by **0.46 percent**. The same sixteen cells with the interconnect deleted sit at
12.895 MHz; with it they span 12.836 to 12.875 MHz.

The generalisation worth keeping: **a partition is cheap exactly where the circuit already has a
high impedance or a series blocking element, and expensive where it has a resonator.** Look for the
DC block, not for the mechanical convenience.

## Common-mode versus per-unit is the real distinction

The harness detunes all sixteen lines and the spine detunes them unequally, and only the second one
is a problem.

A common term is absorbed by choosing the nominal capacitor. A per-unit term is not, because every
board is one design. So `HARNESS_LENGTH_MM` being **equal** across the harnesses matters more than
it being short, which is the opposite of the instinct, and it is why that constant exists rather
than a per-position length.

What remains per-unit is a board's place in the chain: the first taps the bus one harness from the
reader, the fourth four harnesses and three boards away. That spread is 0.77 percent against a
2 percent limit, inside what the DNP trim pads already on every lane take out. Those pads were put
there for tolerance and turn out to pay for the topology.

## How many pieces is a different question from where to cut

Sixteen strips was designed and built first, and it worked electrically. It was superseded on
arithmetic that has nothing to do with RF: sixteen strips need sixteen connectors plus two spine
boards with twenty more, and thirty-six connectors was the **entire** parts-cost increase over the
monolith. Four boards of four lanes need eight.

The lesson generalises past this board. When a partition's unit cost is dominated by the
*interface* rather than the *content*, the right block size is set by connector count, not by how
finely the content divides. Sixteen is the most flexible cut and four is the cheapest, and nothing
about the electrical argument distinguishes them.

Eight lanes per board would be cheaper still on connectors and is ruled out by something else
entirely: 280 mm wide puts it back inside the fabricator's size charges. Three constraints, three
different units, and the answer sits where they cross.

## Splitting costs substrate, structurally

The monolith carries rows on front copper and columns on back: 90,000 mm2 of substrate holding two
planes of antenna. Any split uses one face per board and wastes the other, so it buys **1.87 times**
the area no matter how it is drawn. This is not a layout inefficiency to be
optimised away, and recognising that early stops a lot of wasted redrawing.

The offsetting effect is a size-driven surcharge rather than area, and it turned out to be larger
than the penalty. A 300 by 300 mm board pays 50.47 EUR of large-size assembly charge, 61.5 percent
of its PCBA. A 300 by 33 mm board pays **zero**. Both are 300 mm long, so length alone is not the
trigger, but two data points cannot separate width from area and no more were bought. The practical
consequence is that panelising strips may reincur the charge that separate strips avoid, so a panel
has to be quoted rather than assumed free.

Quoted 2026-08-02: one working sensing plane is 20.92 EUR in bare copper against the monolith's
58.34. The split is cheaper despite buying almost twice the substrate. A 300 by 140 mm board prices
at the same EUR per square millimetre as a 300 by 33 mm one, so 140 mm is still outside whatever
the band measures.

The second-order effect is the vendor's five-piece minimum, and it is not a detail. It forces four
unusable 300 by 300 mm boards to get one, where twenty strips is a set plus spares. When a design
is measurement-bound, the minimum order quantity belongs in the cost model next to the unit price.

## Plane separation becomes a parameter

On one substrate, row-to-column separation *is* the board thickness. Split onto two substrates it
becomes independent of it, and can move in both directions.

That freedom was deliberately not used. `INTERPLANE_GAP` is set so the split reproduces the
monolith, 1.035 mm against 0.965 mm, because every coupling figure in
[[../../../../docs/hardware/criteria.yaml|criteria.yaml]] was extracted at that separation and
moving it would have invalidated them at the same moment as changing the board. Two changes at once
is one unreviewable change.

Re-solving all sixteen loops on the new stackup through the same FastHenry model as
[[row-column-antenna-matrix-technique|the monolith's extraction]] returns identical self inductance
(566.6 nH), identical adjacent-line coupling (0.1401, unavoidable since adjacent lines share a
plane), and worst row-to-column coupling of 0.0652 against 0.0664. The split spends no coupling
margin. The extraction survived the repartition from sixteen boards to four untouched, because the
loops never moved.

The direction of the trade, for later: closing the gap improves the read budget and worsens
row-to-column coupling, which already sits at 3.9 times the [[nfcgameboard-pcb|nfcgameboard prior
art]]. Opening it does the reverse.

## Why this was worth doing at all

Not modularity. The open question on the sensing plane is `LOOP_INSET`, and it is a
single-parameter sweep on per-line geometry with three unresolved outcomes. On the monolith, an
attempt costs five 300 by 300 mm boards at 58.34 EUR. On four-lane boards it costs 20.92.

The minimum order quantity is doing as much work here as the unit price, and it is the thing a cost
model built from EUR per square millimetre would miss entirely: the vendor's five-piece floor forces
four unusable monoliths to get one, while five small boards is a set plus a spare.

The architecture that is cheapest to *change* is a different question from the one that is cheapest
to *build*, and when the design is measurement-bound rather than analysis-bound, the first question
is the one that decides.

## What the split does not fix

The 74HC595 `SRCLR_N` trap survives intact: the seven-conductor hub link has no spare conductor and
the hub does not route the net to its connector anyway. Shifting a known sixteen-bit pattern remains
the driver's mandatory first action.

Hand population gets slightly worse, 176 placed references against 165, and the parts bill rises
4.80 to 7.28 EUR, almost all of it connectors and the four registers.

And it costs a firmware change the sixteen-strip layout did not. Four eight-bit registers chained is
a 32-bit shift where two of them is 16, so the block size reached back into software. Worth
remembering that a partition chosen on fabrication economics can move a boundary in a different
discipline.
