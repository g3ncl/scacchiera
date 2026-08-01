---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
source_file: "Datasheets/PS-43045-M1_MOLEX-VIA-OCTOPART.pdf"
source_title: "Molex PS-43045 Micro-Fit dual row connectors, product specification revision M1, 2007-11-21, bundled with the 43030-0006 terminal drawing"
publisher: "Molex, retrieved from an Octopart mirror"
---

# Micro-Fit 3.0 current rating

Fills the gap [[micro-fit-3-0-mating-evidence]] left open: that page binds mating compatibility and
the wire range and says in its own last line that it qualifies nothing else, so no current rating
stood behind the highest-current path in the product. It does not close the gap. See the provenance
warning below.

[document::PS-43045] [revision::M1] [date::2007-11-21]

## Ratings recorded

Section 4.2, current and applicable wires:

| AWG | Amps |
| --- | --- |
| 20 | 5 |
| 22 | 5 |
| 24 | 4 |
| 26 | 3 |
| 28 | 2 |
| 30 | 1 |

**The table stops at 20 AWG. This revision has no 18 AWG row.** Maximum outside insulation diameter
is 1.85 mm for 20 to 24 AWG, which matches the 1.85 mm already recorded for the bound
[[430300038]] terminal.

Section 4.2's own preamble: current depends on connector size, contact material, plating, ambient
temperature and board characteristics, and "actual current rating is application dependent and
should be evaluated for each application".

Section 4.3, temperature: -40 to +105 degrees Celsius operating, **including terminal temperature
rise**.

The bundled 43030-0006 terminal drawing states 250 V, **5.0 A maximum**, 10 milliohm maximum contact
resistance. That terminal is the 20 to 24 AWG variant, not the fitted 18 AWG one.

## Why this does not settle the question

1. **Provenance.** This is an Octopart-hosted copy, not a file retrieved from Molex.
   `molex.com` and `tools.molex.com` both failed to serve over repeated attempts from this machine.
   Vault rules want the manufacturer's own file, so this is a stopgap that must be replaced.
2. **Revision.** M1 is dated 2007. Later revisions of PS-43045 are known to carry an 18 AWG row and
   a Current Derating Reference Information table indexed by circuit count and by wire-to-wire
   versus wire-to-board. Neither is in this copy.
3. **Wrong variant.** The fitted terminal is [[430300038]], the 18 AWG version. Distributor listings
   put it at 8.5 A, but a catalog figure is not a datasheet figure and this project does not bind
   electrical limits from listings.

## Consequence for the design

The cell harness carries 5.871 A peak through a single Micro-Fit contact pair.

- If 8.5 A is the correct figure for the fitted 18 AWG terminal, the margin is about 31 percent and
  the harness is fine.
- If 5.0 A governs, the harness is about 17 percent **over** rating on the highest-current path in
  the product.

Nothing here decides between those. What is needed is the current revision of PS-43045 from Molex,
including its derating table for a two-circuit wire-to-board housing with every circuit energized,
which is the worst arrangement this connector sees here.

## Related

- [[micro-fit-3-0-mating-evidence]]
- [[430300038]]
- [[430250200]]
