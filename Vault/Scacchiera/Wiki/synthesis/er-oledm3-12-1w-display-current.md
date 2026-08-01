---
type: synthesis
tags:
  - wiki/synthesis
date_updated: 2026-08-01
---

# Is the display 320 mA or 2 mA?

**Question.** [[er-oledm3-12-1w]]'s datasheet section 4.3 gives 320 mA maximum at 3.3 V with the
whole display active and 2 mA maximum in sleep. The BuyDisplay product page instead labels 2 mA as
the module maximum. The load budget assumes 320 mA per display, and two displays are fitted. Which
figure is right?

**Answer. 320 mA is right. The product page has published the sleep figure as the maximum.** The
design's existing assumption stands, and it stands for a reason now rather than only because it
was the conservative direction.

## Argument 1: 2 mA is not physically possible

2 mA at 3.3 V is 6.6 mW for the entire module. That has to cover the SSD1362 controller, the
onboard boost converter that generates the panel's high-voltage rail, and 16384 lit pixels. A
boost converter's own quiescent draw is in that range before it delivers anything. No 3.12 inch
PMOLED lights from 6.6 mW.

## Argument 2: an independent panel of the same size agrees with 320 mA

[[w256064-xalg-datasheet]] is a 3.12 inch 256 by 64 PMOLED from Electronic Assembly, different
manufacturer, different controller, and it publishes the current table the bound part's product
page garbles. Working from its numbers to an equivalent 3.3 V input current:

- 32 mA typical at VCC = 14.5 V on a 50 percent checkerboard is 464 mW.
- 100 percent fill lights about twice the pixels, so roughly 928 mW.
- Delivered through a boost from 3.3 V at 85 to 90 percent efficiency, that is **312 to 331 mA**.

Against the datasheet's 320 mA. Using the max column instead of typical gives 415 to 439 mA, and
using a 12 V panel rail gives 194 to 274 mA, so the plausible band is roughly 195 to 440 mA and
320 mA sits inside it near the middle. The two documents agree.

## Evidence class

This is **Derived**, not Datasheet. The bound part's own datasheet already says 320 mA; what is
derived here is the demonstration that the product page contradicting it is the erroneous one.
Nobody at the supplier has confirmed the error.

## What this does and does not close for V1

Closes: the load budget's 320 mA per display is no longer an unresolved contradiction between two
manufacturer documents. It is a documented product-page error with independent corroboration.

Does not close:

1. The original manufacturer PDF is still not filed. `buydisplay.com/download/manual/` returns
   HTTP 403 to automated clients, including with ordinary browser headers and referer. Search
   engines index the path, so it is public and merely bot-blocked; a human opening the URL in a
   browser and saving it to `Datasheets/` resolves this in a minute. No attempt was made to
   circumvent the block.
2. The filed datasheet revision is **1.0, preliminary, dated 2025-08-07**. V1's definition of done
   treats a provisional document as a release blocker in its own right, independently of the
   current-draw question. A preliminary datasheet is grounds to hold, and this has not been
   recorded as a blocker before now.
3. The exact 16-to-7-pin cable and the module interface straps are still unbound.

## Related

- [[er-oledm3-12-1w]]
- [[w256064-xalg-datasheet]]
- [[ssd1362]]
