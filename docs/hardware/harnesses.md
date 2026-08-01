# Harnesses

Every cable in the product, what it carries, and what has to be true before one can be ordered or
crimped. The connectors on each board are bound and audited; the cables between them are not, and
this file is the open list. Board-side pin orders live with each board:
[hub.md](hub.md), [display-interface.md](display-interface.md),
[power-module-interface.md](power-module-interface.md).

## Inventory

| Harness | Connector | Contacts | Worst-case per contact |
| --- | --- | --- | --- |
| Cell to power board | Molex Micro-Fit 3.0, 2-circuit, 430250200 with 430300038 | 1 pair | **5.871 A** |
| Power module to hub (J3) | Micro-Fit 3.0, 8-circuit, 430250800 with 430300038 | 2 supply, 2 ground, 3 signal, 1 NC | 1.0 A |
| Hub to power module (J2) | JST GH 1.25, 7-way | 3 supply, 4 ground | 0.67 A |
| Hub to matrix (J4) | JST GH 1.25, 7-way | 1 RF, 1 supply, 2 ground, 3 signal | below 0.1 A |
| Hub to display, two off (J5, J6) | JST GH 1.25, 7-way | 1 supply, 1 ground, 5 signal | 0.32 A |
| Hub to light bar, two off (J7, J8) | JST GH 1.25, 4-way | 1 supply, 1 ground, 2 data | 0.224 A |
| Hub UART service (J9) | JST GH 1.25, 4-way | 1 supply, 1 ground, 2 signal | below 0.1 A |
| Cell thermistor | 2-pin | 2 | microamps |
| Button | 2-pin | 2 | microamps |

The two harnesses that carry real current are the cell link and the module output. Everything else
is signal or a few hundred milliamps.

Two derivations worth keeping, because both looked like problems and are not:

- **J2 is not marginal.** Its three supply contacts looked at first like 3.0 A over a 1 A-per-contact
  JST GH, which would be at the rating with no margin. It is not: `functional/power.md` caps the
  source at a compliant 5 V, 2 A USB supply, so the real figure is 0.67 A per contact with the
  return spread over four grounds. The "3.0 A capability" in
  [power-module-interface.md](power-module-interface.md) is the connector's capability, not the load.
- **Cell-lead drop is negligible.** 18 AWG at roughly 21 milliohm per metre over a 0.25 m round trip
  is about 5 milliohm, so 30 mV at 5.871 A. It does not eat into the 2.87 V boost floor.

## The cell harness: 18 AWG on a single pair

**18 AWG wire into 430300038 terminals, a single contact pair, rated 8.5 A.** The harness carries
4.442 A RMS, so the margin is about 48 percent.

### The comparison is RMS, not peak

A connector current rating is a thermal limit. Molex bases its deratings on not exceeding a
30 degree Celsius temperature rise, and contact heating is I squared R, so the figure to compare
against is the **RMS** current, not the switching peak.

| Quantity | Value | Source |
| --- | --- | --- |
| Battery-path RMS | **4.442 A** | `POWER-CELL-PASS-FET-LOSS` operating conditions |
| Boost inductor peak | 5.871 A | `POWER-BOOST-INDUCTOR-PEAK` margin |
| Contact rating, 18 AWG | 8.5 A | distributor listings for 430300038, see the caveat below |

The 5.871 A figure is a 500 kHz inductor peak. It sizes the converter's current limit and the
inductor's saturation rating; it does not heat a contact.

### The one caveat, recorded rather than treated as a blocker

8.5 A comes from distributor listings, not from a datasheet in `Datasheets/`. Molex PS-43045
revision M1 is filed and its table stops at 20 AWG at 5 A with no 18 AWG row, and Molex's own
servers did not respond to repeated attempts. See
[micro-fit-current-rating](../../Vault/Scacchiera/Wiki/sources/micro-fit-current-rating.md).

This is deliberately not treated as a blocker, because **the harness passes under either candidate
figure**: 48 percent margin at 8.5 A, and still 11 percent at 5.0 A. The unresolved rating changes
how much room there is, not whether the design works. Record the evidence class as catalog rather
than datasheet until a current Molex revision is filed, and prefer 18 AWG regardless, since at
21 milliohm per metre against 20 AWG's 33 it is the lower-loss wire.

Watch the insulation, though: the terminal caps insulation outside diameter at 1.85 mm, and plenty
of ordinary 18 AWG is jacketed thicker than that.

### Why a single pair is right here

A single positive and a single negative is the normal way to connect a cell, not a compromise.
Every battery interconnect in general use is a single pair, most of them carrying far more than
4.4 A.

[power-module-interface.md](power-module-interface.md) says "power and ground use multiple contacts
so no single terminal carries the whole interface current", but that is about the board-to-board
links J2 and J3, where the connector already has pins to spare and paralleling costs nothing. It is
not a rule about connectors in general, and it does not apply to a two-wire battery link. Doubling
contacts is also weaker than it looks: paralleled contacts do not share current evenly because
their resistances differ, so two contacts are worth appreciably less than twice one. The right
answer for a battery link that needs more current is a larger connector, not more pins of a small
one, and this one does not need either.

## What is still open for every harness

The connectors are bound. None of the cable is:

- **Wire.** Type, temperature rating, strand count and insulation diameter. The 430300038 terminal
  accepts 18 AWG or 0.75 square millimetre with insulation at most 1.85 mm, which rules out plenty
  of ordinary 18 AWG.
- **Crimp.** Molex names hand tool 63828-0200 for this terminal and wire range. Either that tool is
  bought and the crimps are qualified by pull test, or pre-crimped leads are sourced and bound as
  parts. Hand-crimped power terminals with no pull-test evidence are the kind of thing V8 discovers
  the hard way.
- **Colour coding.** No convention is recorded. It matters most where a reversed connection is
  physically possible and electrically bad, which the keyed housings are supposed to prevent but
  colour coding catches during assembly rather than after.
- **Length and strain relief.** Both follow from the rail arrangement, which is not drawn yet.
- **The assembled article.** Nothing above is evidence until a built harness is measured.

## V8

The cell harness is the one to instrument: contact temperature rise at 5.871 A with both circuits
energized, and voltage drop end to end. The rest can be continuity and mating checks.
