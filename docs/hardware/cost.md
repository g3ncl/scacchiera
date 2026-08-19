# Electronics cost

What one complete board costs in electronics, where the money actually is, and which levers are
worth pulling. Component figures are generated from the schematics; fabrication and assembly
figures are quoted where a quote exists and marked where one does not. Nothing here is a price
list, and every estimate says so.

Mechanical cost (filament, fasteners, the printed enclosure and the pieces) is out of scope: it is
owner-managed per V7 and priced in plastic rather than in parts.

## Evidence classes

Read the class before the number.

| Class | Means |
| --- | --- |
| **Quoted** | A JLCPCB quote exists at a recorded date. |
| **BOM** | Generated from the schematic by `hardware/pcb/bom.py`; an engineering estimate at catalog unit prices, excluding attrition, shipping and tax. |
| **Estimated** | Neither. A bounded guess, present so the total is not silently missing a line. |
| **Unpriced** | No figure at all. These are the holes. |

## One complete board

### Custom PCBs

All four boards are quoted. Fabrication quantity 5, assembly quantity 2.

| Item | Cost | Class |
| --- | ---: | --- |
| Sensing plane, 5 quad boards bare, 0.6 mm, OSP, black | 20.92 EUR | **Quoted 2026-08-02** |
| Hub, complete: bare PCB, assembly and factory components | 44.88 EUR | **Quoted**, J1 unresolved, see below |
| Power board, complete: bare PCB, assembly and factory components | 29.70 EUR | **Quoted** |
| Light bars, bare, 5 pieces | 4.08 EUR | **Quoted** |
| **Boards subtotal** | **99.58 EUR** | |
| Hand-fitted parts, all four boards, 270 references | 29.11 EUR | BOM, understated, see below |
| **Subtotal** | **128.69 EUR** | |

### What the two board quotes taught the model

**The X-ray prediction was wrong.** This file predicted a 2.85 EUR X-ray inspection line on the
power board because it carries two QFNs, on the reasoning that the hub was charged for QFNs. **The
power quote has no X-ray line at all.** So the trigger is not "a QFN is present": the hub has a
QFN-40 at 40 pins plus a module with a hidden ground-pad array, and the power board's QFN-24 and
QFN-20 did not attract it. Treat X-ray as a hub-class charge tied to pin count or hidden arrays,
and as unpredictable in general: quote it, do not model it.

**De-panelising cost nothing, and the panel's fabrication saving was never real.** The two small
boards came back at 1.74 and 4.08 EUR, and the power board's PCB line is a "Special Offer" with
**no engineering fee at all**. This file had charged the split an extra 3.47 EUR engineering fee;
that did not happen. Small boards get promotional fabrication pricing, and the panel was buying
nothing on the fabrication side.

What the panel *would* still save is on the **assembly** side, where the hub and power board each
paid their own 7.10 setup and 1.33 stencil. That is about 8.40 EUR of genuine duplication and it is
the only part of lever 2 that survives. It is also the part that needs panelised CPL support and a
panel that works.

**Components are about three times the BOM estimate on this board.** 10.44 EUR charged for 16 items
against 3.62 EUR of catalog unit prices, a wider gap than the hub's roughly two times. The single
worst line is the 22 uF 0805 Basic capacitor, C45783, at 2.92 EUR for ten pieces: this file already
recorded it as expensive-but-unavoidable, and the quote confirms it is 28 percent of the board's
whole component cost.

**Everything else landed.** 16 unique parts detected exactly as predicted, so nothing was
unselected; three Extended parts at 8.00 EUR against a nominal 8.10; setup, stencil, SMT and
nitrogen all within a few cents of the hub's figures.

### Purchased accessories

Parts on no board BOM, without which the product does not work.

| Item | Cost | Class |
| --- | ---: | --- |
| Two ER-OLEDM3.12-1W display modules | about 31 EUR the pair | Catalog, unconfirmed, see below |
| 32 AD Circus SLIX2 tags, at 0.69 each in ones | 22.08 EUR | Catalog (Shop NFC) |
| Protected 1S 21700 cell assembly | about 11 EUR | Catalog candidate, not bound |
| Four JST GH harnesses for the sensing chain | about 6 EUR | Estimated |
| Micro-Fit housings and 18 AWG terminals | about 5 EUR | Estimated |
| 2.4 GHz FPC antenna with MHF3 pigtail | about 2 EUR | Estimated |
| **Subtotal** | **77.08 EUR** | |

### What you buy and solder yourself

The parts tables above include the hand-fitted parts. They are not a separate cost, but they are a
separate **purchase**, from a different supplier, and that is worth seeing on its own:

| Board | Hand refs | Parts cost |
| --- | ---: | ---: |
| Light bars, two | 60 | 12.66 EUR |
| Sensing plane, four boards | 176 | 7.28 EUR |
| Hub | 23 | 5.14 EUR |
| Power board | 11 | 4.03 EUR |
| **Total** | **270** | **29.11 EUR** |

**That 29.11 EUR is an understatement, and structurally so.** It is the engineering BOM's catalog
unit price times quantity, which is the price at assembly quantities with no attrition. Buying the
same parts yourself adds three things it does not model:

- **Minimum order quantities.** Nobody sells eleven 0603 resistors. Reel and strip minimums mean
  the paid quantity is often 10x the fitted one, though at these unit prices the absolute effect is
  small.
- **Retail markup**, since LCSC or DigiKey retail is not the JLC assembly price.
- **A second shipment**, roughly 10 to 20 EUR, from a different supplier than the boards.

The shipment is the term that matters and it is larger than the parts. Treat the hand-fit purchase
as **about 45 to 55 EUR delivered**, not 29.

### Not in either subtotal

Shipping and tax. One JLCPCB shipment to the EU is roughly 15 to 25 EUR and Italian VAT is
22 percent, so the delivered total is meaningfully above the sum of the tables. **Both scale with
the number of separate orders**, which is why order consolidation appears in the levers below.

### Total

**205.77 EUR at listed prices**, of which **99.58 is quoted** and the rest is catalog or estimate.

| | |
| --- | ---: |
| Boards, all four, quoted | 99.58 EUR |
| Hand-fitted parts, 270 references | 29.11 EUR |
| Purchased accessories | 77.08 EUR |
| **Total** | **205.77 EUR** |

That is the sum of listed prices, not a delivered cost. Add the LCSC shipment for the hand-fit
parts, the JLCPCB shipment, and 22 percent Italian IVA, and **a realistic delivered figure for the
first unit is 270 to 300 EUR** once J1 is resolved.

Still outside the total: **J1**, the hub's USB-C receptacle, which the matcher rejected. Whatever
replaces it adds a part and possibly a feeder change.

### The displays, corrected

An earlier revision of this file guessed the two display modules were probably the largest line
item in the product and might rival everything else combined. **That guess was wrong.** A 2026-08-02
supplier check puts the ER-OLEDM3.12-1W at roughly USD 17, so the pair is about **31 EUR**, in line
with the light bars rather than dominating anything.

Recorded as **unconfirmed**, deliberately. The figure comes from a marketplace listing that offers a
choice between the bare panel (ER-OLED3.12-1W) and the module (ER-OLEDM3.12-1W), and the two are
different products at different prices. The manufacturer's own product page returned HTTP 403 to
automated retrieval, so nothing is filed in `Clippings/`. **Confirm the module price against
EastRising directly before using it**, and file the capture when you do.

The correction matters mostly because it retires a lever. There is no 50 EUR sitting in the display
choice, so switching to a smaller panel or dropping to one display buys far less than it appeared
to and costs a functional-spec change either way.

## Where the money is

Now that every board is quoted, the ranking is measured rather than estimated.

1. **The two assembled boards, 74.58 EUR between them.** The hub at 44.88 and the power board at
   29.70, and in both cases the *board* is nearly free: 6.60 and 1.74 of fabrication against 38.29
   and 27.96 of assembly. **Assembly is 88 percent of what the assembled boards cost.**
2. **Purchased accessories, 77.08 EUR**, the largest single block and entirely outside every board
   BOM. Displays, tags and the cell dominate it.
3. **Fixed assembly charges, about 33 EUR of the 74.58.** Two setups at 7.10, two stencils at 1.33,
   two nitrogen lines and 16.00 of feeder fees. None of it scales with how many boards you build.
4. **The hand-fit parts purchase, 45 to 55 EUR delivered**, of which more than a third is a
   shipment rather than parts.
5. **The sensing plane, 28.20 EUR all in**, was the assumed dominant cost when this file was
   written and is now the *cheapest* major item. That is what this branch did.
6. **Bare fabrication is nearly free at this scale.** All four boards together cost 33.34 EUR of
   fabrication, and two of them qualified for promotional pricing with no engineering fee.

**The shape of the total changed once the displays were priced.** No single component dominates.
What dominates is *per-order and per-shipment fixed cost*, which is why the levers below are mostly
about consolidating orders rather than about choosing cheaper parts.

## Levers, most valuable first

### 1. Consolidate shipments, the biggest lever in the product

**Estimated saving: 30 to 60 EUR.** With no dominant component, the largest controllable cost is
the number of parcels. A naive build orders sensing boards, the assembled panel, hand-fit parts,
displays, tags and a cell from six places.

**One order for everything is not possible**, and it is worth knowing why before trying: no
supplier carries PCB fabrication, an EastRising OLED module, an Avery Dennison NFC inlay and a
protected lithium cell. The cell is the hardest of these and the reason is regulatory rather than
commercial: protected lithium cells carry UN 38.3 transport restrictions and are effectively
un-consolidatable with an air shipment from China.

The achievable floor is **four parcels, of which one carries most of the value**:

| # | Order | Contents |
| ---: | --- | --- |
| 1 | **JLCPCB + LCSC, combined into one shipment** | All five board designs, bare and assembled, **plus all 270 hand-fit parts**, plus the JST GH cable assemblies and the FPC antenna |
| 2 | buydisplay.com | Two ER-OLEDM3.12-1W modules; nobody else carries them |
| 3 | shopnfc.com | 32 (buy 50) AD Circus SLIX2 tags. Italian, domestic, cheap to ship |
| 4 | nkon.nl | Protected 21700 cell. EU, and the one item that cannot travel with the rest |

**Order 1 is the win, and it is an explicit supported feature.** LCSC and JLCPCB are the same group
and will merge two orders into one shipment: place both, then send the LCSC and JLCPCB order
numbers to `support@lcsc.com` and ask them to combine, or bind an existing JLCPCB order during LCSC
checkout. Both orders must share a currency and a customer ID. Shipping is recalculated on the
merged parcel. **Once combined the orders cannot be split or unbound**, and the merge fails if the
LCSC order has already shipped, so combine before either moves.

That collapses the two largest and heaviest orders into one parcel and one customs event. Parcels 3
and 4 are EU-domestic, cheap, and carry no customs step at all.

**Prefer IOSS-registered sellers into Italy.** LCSC and the large marketplaces collect the 22
percent IVA at checkout; a seller who does not leaves the courier to collect on delivery and add a
handling fee of 5 to 15 EUR on top. Same tax, worse total.

### 2. Put the hub on the light-bar and power panel

**Estimated saving: about 9 EUR of assembly fees plus one shipment, so 25 to 35 EUR delivered.**

The hub and the power board are the only two boards that go to factory assembly, and they currently
go as two separate fabrication and assembly orders. Both are 1.0 mm, 2 layers, and adding the
162 x 46 mm hub to the existing 130 x 63 mm panel gives roughly 167 x 113 mm, comfortably inside
any size band. One panel means one engineering fee, one
assembly setup, one stencil and one shipment instead of two of each.

Per-order fixed cost, from the 2026-07-25 hub quote's structure:

| Line | Separate orders | One panel |
| --- | ---: | ---: |
| Setup | 14.38 EUR | 7.19 EUR |
| Stencil | 2.68 EUR | about 1.50 EUR |
| Extended feeders | 18.90 EUR | 18.90 EUR |
| SMT, nitrogen | about 4 EUR | about 2 EUR |
| **Total service fees** | **about 40 EUR** | **about 30 EUR** |

The feeder line does not move, because feeders are charged per unique Extended part and the two
boards share none. Everything else halves. `hardware/pcb/panel.py` already generates the existing
panel from the routed boards, so this is a change to which boards it takes, not a new mechanism.

The obvious objection is real and worth stating: **the light bars are hand populated**, so a panel
going to assembly is placing parts on one third of its own area. That is already true today with
the power board, and it costs nothing extra, because the CPL decides what gets placed.

### 3. Re-quote the hub, its Extended count is stale

**Estimated saving: about 8 EUR, already designed in but not yet reflected in any quote.**

[jlcpcb-sourcing.md](jlcpcb-sourcing.md) records 18.88 EUR of feeder fees against seven Extended
factory placements on the historical MCP73871 hub. The current hub has **four**: J1 (USB-C),
U3 (PN5180), U4 (ESP32-C6-MINI-1U) and Y1 (the crystal). At 2.70 EUR each that is 10.80 EUR. The
saving is real but it is bookkeeping, not a new decision, and the register already warns that the
quote predates the design.

The same recount applies to the power board, which has three: Q1, U1 and U2.

### 4. Buy 50 tags rather than 32, which is not a saving and is worth doing anyway

**Costs 2.42 EUR, buys 18 spares.** 32 tags in ones is 22.08 EUR at 0.69 each. Fifty crosses into
the 0.49 tier at 24.50 total, so the absolute spend goes *up*, not down; the 100+ tier at 0.34
would be 34 EUR for a hundred. Listed here because the tier structure invites a saving that is not
there, and because the spares matter: a tag is glued into a printed piece and a bad bond is not
recoverable.

### 5. Consolidate every board into one order

**Estimated saving: 15 to 25 EUR per shipment avoided.** The sensing plane is bare copper, the
panel is assembled, and they are different fabrication specifications (0.6 mm against 1.0 mm), so
they cannot share a panel. They can still share an order and a shipment. With lever 2 applied the
whole product is two fabrication items in one order.

## Closed and rejected

Recorded so they stop being re-proposed.

### Sensing-plane thickness, closed at no cost

**Resolved 2026-08-02, saving nothing because nothing was being lost.** 0.6 mm on a 300 mm outline
was the last open fabrication risk on the shipping board, and thin stock on a long outline is
exactly where fabricators add handling charges. Priced against 0.8 and 1.0 mm at the same outline
and quantity: **all three are the same price.** Take 0.6 mm.

Kept here because the escape route is the interesting part and it remains available if a later
fabricator prices differently. Row-to-column separation is what every coupling figure in
[criteria.yaml](criteria.yaml) depends on, and it is `QUAD_THICKNESS + INTERPLANE_GAP = 1.0 mm`.
The split is what made those two terms independent, so **0.8 mm board with a 0.2 mm frame rib gives
the identical 1.0 mm separation**. FR4 and air are both non-magnetic, so swapping one for the other
at 13.56 MHz does not move the coupling, and `test_quad.py` asserts the separation rather than the
thickness, so the invariant is already guarded. The one cost is that `quad_rf.py` derives the
on-board bus inductance from `QUAD_THICKNESS`, so `test_sim_quad.py` would need rerunning against
criteria currently passing at 0.99 percent of a 2 percent limit.

That optionality is a dividend of the partition nobody designed for: the monolith's plane
separation *was* its board thickness, so it had no such escape.

### Swapping the fee-carrying parts for fee-free ones, which cannot be done

**Available: 0.00 EUR of 18.90.** Settled 2026-08-02 against the catalog rather than argued, and
recorded here so it stops being re-proposed.

First, the target set is wider than "Basic". JLCPCB waives the feeder fee for **Preferred Extended**
parts as well, so the real question is whether a part is in the *economic* catalog, Basic and
Preferred Extended together. That catalog is captured at
`Vault/Scacchiera/Clippings/jlcpcb/economic-parts-2026-08-02.csv` and summarised in
[the vault summary](../../Vault/Scacchiera/Wiki/sources/jlcpcb-economic-parts-2026-08-02.md): 1586 live parts, 351 Basic and 1235 Preferred Extended.

**None of the seven fee-carrying parts appears in it**, in either the 07-24 or the 08-02 capture.
The category breakdown says why, and it is more decisive than any per-part argument:

| Count | Category |
| ---: | --- |
| 1482 | diodes, circuit protection, resistors, capacitors, transistors |
| 22 | Power Management (PMIC) |
| 7 | Crystals |
| 6 | Embedded Processors & Controllers |
| **0** | **Connectors** |
| **0** | **Modules** |

**The fee-free catalog is passives and discretes.** It contains no connector of any kind and no RF
or MCU module at all, so hub J1 (USB-C) and U4 (ESP32-C6-MINI-1U) are not hard swaps, they are
impossible ones. Its seven crystals include two in the exact 3225 footprint and neither is 27.12
MHz, the frequency PN5180 Table 142 fixes. Its 22 PMIC parts contain nothing resembling a BQ25895
or a TPS61088.

The one part with a real pool is power Q1, the reverse-polarity pass FET, against 16 fee-free
P-channel MOSFETs. **All sixteen are SOT-23 at 33 to 45 milliohm.** At the 4.442 A RMS this stage
carries that is 0.65 to 0.89 W in a package rated 1.2 to 1.5 W, against a CSD25404Q3 chosen partly
for its thermal behaviour, in a stage whose junction-temperature bound already sits at 96.5 degrees
ambient. Not a substitution; a downgrade that would need the reverse-battery bench and the
junction-temperature analysis rerun to save 2.70 EUR.

**The structural reason, which generalises past this project.** Every one of the seven is
factory-placed for the same recorded reason: *pads under the body or too fine a pitch*. The parts
an iron cannot reach are QFNs, modules, clipped FETs and connectors, and those are exactly the
parts too complex to be economic. **The set you cannot hand-fit and the set you pay feeder fees for
are nearly the same set**, so the fee is a floor rather than an optimisation target. The available
reduction already happened, when the build plan moved every iron-reachable Extended line to hand
fitting and took the hub from seven feeders to four.

Membership of the economic catalog did not change at all between the two captures, only price and
stock, so this answer is stable on a scale of weeks rather than needing a recheck per order.

Correcting an earlier revision of this file: it named the USB-C connector as a viable candidate
worth 2.70 EUR. That was wrong. There are no fee-free connectors.

**There is a different route to the same 2.70 EUR, though, and it is open.** A part does not have
to be fee-free to cost nothing: it can be hand-fitted instead, which is how the hub already went
from seven feeders to four. J1 is the only one of the seven where that is even arguable, because
the hub is a power-only sink and a smaller power-only USB-C would carry every contact it uses.
That candidate is written up in
[jlcpcb-sourcing.md](jlcpcb-sourcing.md#open-candidate-a-hand-fittable-power-only-usb-c-for-j1),
including the trap that sinks it if taken carelessly: **the part needs six contacts, not four**,
because CC1 and CC2 must stay separate, and many parts sold as "Type-C 6P" have no CC contacts at
all. The saving is still 2.70 EUR and the real argument is repairability rather than cost.

### The purchased power module

**Not recommended, recorded because it will be asked.** [power-subsystem.md](power-subsystem.md)
treats a purchased 5 V module as the superseded option. The custom power board costs 7.65 EUR of
parts plus three Extended feeder changes (8.10 EUR) plus its share of setup, so call it 20 EUR
delivered against roughly 12 to 15 EUR for a purchased module of similar capability.

The margin is thin and it moves the wrong way once the module has to meet
[power-module-interface.md](power-module-interface.md): the custom board exists because no surveyed
module provided the independent cell-temperature interlock and the 2 A regulated output together,
and V3 evidence has since been built against the BQ25895 and TPS61088 specifically. Buying a module
now would discard simulation work worth more than the 5 EUR it saves. **Revisit only if the module
survey turns up a compliant part**, not for the price.

### Individual line items

- **The four 74HC595 registers**, half of whose outputs are unused. The waste is 0.40 EUR. Using
  eight lanes per board to halve the register count means a 280 mm outline, back inside the
  fabricator's size charges that cost 50.47 EUR. See [quad.md](quad.md).
- **The 22 uF 0805 Basic capacitor** at a high unit price. An Extended alternative must beat its own
  2.70 EUR feeder fee before it saves anything, and it does not.
- **The 10 uH matrix choke's margin.** Its Basic part is rated 15 mA against a simulated 10.33 mA
  bias. An Extended part with more headroom buys margin nobody needs for a feeder fee.
- **Hand populating the sensing plane.** Buying the labour back is available now that the outline
  pays no size charge, and the superseded strip quote priced comparable work at about 0.34 EUR a
  joint, which would be roughly 60 EUR against 176 joints. No quote exists for the quad itself.
  Either way it is a time-versus-money call for the builder, not a saving.

## Where to look things up

Checked 2026-08-02. Catalog pages are for stock, price and library class only; an electrical limit
still comes from a filed datasheet, per `CLAUDE.md`.

### The JLCPCB parts library

| Source | Use it for |
| --- | --- |
| [jlcpcb.com/parts](https://jlcpcb.com/parts) | The official library, 700k+ in-stock parts, with a "Basic & Promotional Extended Parts" filter. **Authoritative for library class**, which is the thing that decides the 2.70 EUR feeder fee. |
| [yaqwsx.github.io/jlcparts](https://yaqwsx.github.io/jlcparts/) | **The one to actually use for substitution hunting.** Third-party parametric search over the same catalog: full text, category browse, sort by any attribute, sort by price at a given quantity, direct datasheet and LCSC links. It is the right tool for the Basic-equivalent question under Closed and rejected. |
| [lcsc.com](https://www.lcsc.com) | Retail arm, same inventory pool. The JLC assembly library is a subset of LCSC stock, so an LCSC page confirms a part exists but **not** that JLC will place it. |

**The fee-free catalog is mirrored in the vault**, at
`Vault/Scacchiera/Clippings/jlcpcb/economic-parts-2026-08-02.csv`: 1586 live parts with LCSC code,
library class, package, price, stock and the full parametric string, 771 kB, greppable offline.
It comes from [lrks/jlcpcb-economic-parts](https://github.com/lrks/jlcpcb-economic-parts), which
republishes JLCPCB's Basic and Preferred Extended lists weekly. Refresh with:

```bash
curl -sSL https://lrks.github.io/jlcpcb-economic-parts/economic-parts.csv \
  -o Vault/Scacchiera/Clippings/jlcpcb/economic-parts-$(date +%F).csv
```

File it as a new dated capture rather than overwriting; `Clippings/` is immutable. Query recipes and
the full category breakdown are in [the vault summary](../../Vault/Scacchiera/Wiki/sources/jlcpcb-economic-parts-2026-08-02.md). The full 700k-part catalog
is deliberately **not** mirrored: it is large, and every question this project asks is about the
fee-free subset. Use [jlcparts](https://yaqwsx.github.io/jlcparts/) interactively when a question
genuinely needs the whole catalog.

### Suppliers that ship to Italy

| Supplier | Where | Best for |
| --- | --- | --- |
| **LCSC** | China, IOSS | The 270 hand-fit parts. They already carry LCSC codes on the generated BOM, so the self-solder BOM maps to a cart almost directly. Cheapest by a wide margin. |
| **TME** | Poland, EU | Genuine JST GH and Molex Micro-Fit, cheap and fast into Italy with no customs step. |
| **Mouser**, **Digi-Key** | EU warehouses | The parts already sourced there: the Harvatek light-bar LED, the ESP32-C6-MINI-1U, hub L2. Free shipping over a threshold. |
| **Farnell Italia**, **RS Italia** | Domestic | Next-day when something is missing mid-build. Expensive per part, no customs, no wait. |
| **Reichelt** | Germany, EU | General passives and tools. |

### The specific accessories

| Item | Where |
| --- | --- |
| Display modules | [buydisplay.com](https://www.buydisplay.com) (EastRising direct). **Order-time interface selection may exist here, which bears on a V1 blocker; see below.** |
| Piece tags | [shopnfc.com](https://www.shopnfc.com), Italian, already the vault's price source |
| Protected 21700 cell | [nkon.nl](https://www.nkon.nl), Netherlands, the usual EU source for protected cells |
| JST GH cable assemblies | LCSC, or TME for genuine JST |
| Micro-Fit housings and terminals | TME, Farnell, RS, Mouser |
| 2.4 GHz FPC antenna, MHF3 | LCSC, or Taoglas/Molex via Digi-Key. **MHF3 / W.FL / IPEX3, not U.FL.** |

### A lead on the display interface blocker

[planning.md](../planning.md) records an open V1 item: the module's datasheet conditions every pin
description on "when serial interface mode is selected" and documents no way to select it, so
whether a shipped module talks SPI or 8080 parallel is unknown, and a parallel-strapped module will
not talk to the hub.

The 2026-08-02 supplier check suggests two things bearing on it. The module appears to **default to
8080 8-bit parallel**, which is the feared case rather than the hoped-one. And the retail listing
appears to offer an **interface choice at order time**, alongside a panel-versus-module choice,
which would make this a purchasing question rather than a rework question.

**Both are search-derived and neither is filed evidence.** The manufacturer page returned HTTP 403
to automated retrieval. Treat this as the question to put to EastRising, not as an answer: confirm
the interface option, capture the page, and file it before the blocker is closed.

## What would change these numbers

- **A confirmed display price**, from EastRising rather than a marketplace listing, and for the
  module rather than the bare panel. This is the largest unconfirmed line in the total.
- **A resolved J1.** The hub's USB-C receptacle was rejected by the matcher, so whatever replaces it
  adds a part and possibly a feeder change.
- **A re-quoted hub.** The 44.88 EUR figure carries an Extended count the design has already
  reduced; see lever 3.
- **Any move to more than one unit.** Everything in this file is priced at the five-piece minimum,
  which is one product. The fixed costs (setup, stencil, feeders, engineering fee, shipping) are
  charged once, so a second unit is far cheaper than the first, and a cost model built from this
  page's totals will overstate a second build badly.
