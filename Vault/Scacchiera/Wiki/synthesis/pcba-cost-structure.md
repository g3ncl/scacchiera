---
type: synthesis
date_updated: 2026-08-02
tags:
  - wiki/synthesis
---

# What actually drives PCB assembly cost at one-unit quantity

Written after totalling a whole product's electronics for the first time
([[../../../../docs/hardware/cost.md|docs/hardware/cost.md]]). The useful output was not the total.
It was that the cost model is shaped almost nothing like the bill of materials, and that building
it found a hole nobody had noticed.

Vendor context is [[jlcpcb]] and the part-selection rules in [[jlcpcb-basic-part-sourcing]]; the
board decision it followed is [[split-sensing-plane]].

## The cost model finds the unpriced item

The sensing plane was the assumed dominant cost, and a branch of work cut it from 58.34 EUR to
20.92. Totalling everything else afterwards showed the largest remaining line item was **two
display modules with no filed price at all**, in a project whose rules require a datasheet behind
every bound part.

The lesson generalises past this product. **A cost model's first value is finding what has no
number, not computing the number it has.** An unpriced item hides best while attention is on the
item being optimised, and optimisation attracts attention to exactly the wrong place: the thing
you are measuring is by definition the thing you have measured.

## Almost everything is fixed cost, so cost is a function of order count

At a five-piece minimum, the per-order charges (engineering fee, assembly setup, stencil, feeder
loading, shipping) dominate anything that scales per board. On one quoted example, **42.60 EUR of a
55.36 EUR assembly bill was fixed** and 12.75 EUR scaled across twenty boards.

The consequences run opposite to normal BOM intuition:

- **Two boards on one panel cost roughly one board's fixed charges.** The saving is not
  proportional to how much area or how many parts they share; it is the setup, the stencil and the
  shipment they no longer duplicate.
- **A part count reduction saves almost nothing.** Deleting components moves the small term.
- **Quantity is nearly free.** The second unit of a product is far cheaper than the first, so a
  total built at the minimum order overstates any later build badly.
- **The minimum order quantity belongs in the cost model next to the unit price**, because it
  decides how much of the fixed cost is waste. Five 300 by 300 mm boards to get one usable plane is
  four boards of pure loss; five smaller boards to get a four-board set is a spare.

## Feeder fees are per unique part, which changes what sharing is worth

The vendor charges a feeder change per unique Extended component, not per placement. So:

- **Panelising two boards that share no Extended parts saves setup and stencil but nothing on
  feeders.** All the saving is in the duplicated fixed lines.
- **Panelising boards that share Extended parts saves more**, because the shared feeder is loaded
  once. This is a reason to prefer the same part across boards that goes beyond the usual
  inventory and second-sourcing arguments, and it only appears once boards are considered together
  rather than one at a time.
- **Moving a part to hand assembly deletes its feeder fee entirely.** One project's hub dropped
  from seven Extended factory placements to four purely by hand-fitting everything an iron can
  reach, which is about 8 EUR on a roughly 30 EUR assembly bill. The parts did not change and the
  board did not change.

The corollary nobody likes: the packages that must go to the factory are the ones with pads under
the body (QFN, SON, modules with ground arrays, USB-C, small crystals). Those are also the
expensive parts. **The set of parts you cannot hand-fit and the set you pay feeder fees for are
nearly the same set**, so the fee is close to unavoidable rather than optimisable.

## Size charges are an assembly charge, and there is a separate area premium

Two distinct effects, easy to conflate, and worth separating because they respond to different
changes:

- **A large-size assembly charge** is a step function on the outline, charged on the PCBA line. One
  300 by 300 mm board paid 50.47 EUR, 61.5 percent of its assembly bill; narrower boards paid zero.
  A bare-copper order cannot incur it at all.
- **A bare-fabrication area premium** is separate and gentler. The same large board priced at
  0.130 EUR per 1000 mm2 against 0.100 for the narrow ones, about 30 percent more per unit area for
  being large.

So splitting a large board wins twice, and the two wins have to be argued separately because a
design that avoids one may not avoid the other. What is *not* established from two quoted points is
whether the step function measures width or area, which matters practically: a panel that gangs
narrow boards is wide, and could reincur the charge the separate boards avoided. **Quote the panel
rather than assuming panelisation is free.**

## Related

- [[jlcpcb-basic-part-sourcing]]
- [[jlcpcb]]
- [[split-sensing-plane]]
