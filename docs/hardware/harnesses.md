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

## The cell harness: 20 AWG at the documented 5 A

The cell link is bound to the **documented 20 AWG at 5.0 A** row of Molex PS-43045 rather than to
the 8.5 A that distributors attach to the 18 AWG terminal, because 8.5 A appears in catalog
listings and not in any datasheet available here. Summarized in
[micro-fit-current-rating](../../Vault/Scacchiera/Wiki/sources/micro-fit-current-rating.md).

| AWG | 20 | 22 | 24 | 26 | 28 | 30 |
| --- | --- | --- | --- | --- | --- | --- |
| Amps | 5 | 5 | 4 | 3 | 2 | 1 |

Choosing the documented row changes the terminal. 430300038 is the 18 AWG variant and cannot crimp
20 AWG; the 20 to 24 AWG tin female terminal is **43030-0007** in bag packaging (43030-0001 on
reel), which suits a two-off build. The board-side 43045 headers do not change, so this is a
cable-side substitution with no layout consequence.

### The comparison is RMS, not peak

A connector current rating is a thermal limit. Molex states its deratings are based on not
exceeding a 30 degree Celsius temperature rise, and contact heating is I squared R, so the figure
to compare against is the **RMS** current, not the switching peak.

| Quantity | Value | Source |
| --- | --- | --- |
| Battery-path RMS | **4.442 A** | `POWER-CELL-PASS-FET-LOSS` operating conditions |
| Boost inductor peak | 5.871 A | `POWER-BOOST-INDUCTOR-PEAK` margin |
| Contact rating, 20 AWG | 5.0 A | PS-43045 section 4.2 |

So the cell harness is **inside** its rating at 4.442 A against 5.0 A, with about 11 percent margin.
The 5.871 A figure is a 500 kHz inductor peak and does not heat a contact.

### It is inside, but thinly, and it breaks the project's own rule

Eleven percent is before any derating, and the derating table for a two-circuit housing with both
circuits energized is not in the filed revision. If that derating is as mild as 90 percent the
margin falls to roughly one percent, which is not a margin.

More telling, [power-module-interface.md](power-module-interface.md) already states the principle:
"Power and ground use multiple contacts so no single terminal carries the whole interface current."
J2 gives 5 V three contacts and ground four. J3 gives its output two and two. **The cell link is the
only power interface in the product that puts the whole current through one contact pair**, and it
is also the highest-current one.

Taking the cell connector from two circuits to four, one pair per polarity, puts 2.22 A on each
contact and ends the question outright. It costs a change from the 430450200 header to the
four-circuit part on the power board, and therefore a re-route of that board. That is a real cost
against a harness that currently passes, so it is recorded as a recommendation rather than done.

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
