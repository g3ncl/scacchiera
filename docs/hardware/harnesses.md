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

## The one number that blocks the cell harness

The cell link puts **5.871 A through a single Micro-Fit contact pair**, and no filed source records
what a Micro-Fit 3.0 contact is rated for. [micro-fit-3-0-mating-evidence](../../Vault/Scacchiera/Wiki/sources/micro-fit-3-0-mating-evidence.md)
binds mating compatibility, the 18 AWG wire range and the 1.85 mm insulation limit, and explicitly
says it does not qualify anything else. It carries no current rating and no derating curve.

That has to be read off Molex's own specification before the cell harness is built, including the
derating that applies when every circuit in the housing is energized. Two circuits both at 5.871 A
is the worst arrangement a 2-circuit housing has. Until that number is filed, the cell harness is
an assumption, not a design, and it is the highest-current path in the product.

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
