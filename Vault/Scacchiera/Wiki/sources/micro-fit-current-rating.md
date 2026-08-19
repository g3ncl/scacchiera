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
3. **The previously fitted terminal is absent.** [[430300038]] is the 18 AWG version and appears
   nowhere in this revision. Distributor listings put it at 8.5 A, but a catalog figure is not a
   datasheet figure. Rather than wait, the design moved to the documented 20 AWG row; see below.

## Terminal variants in this document

The 43030 female table, useful now that the design binds the documented 20 AWG row:

| Wire AWG | Plating | Reel | Bag |
| --- | --- | --- | --- |
| 20 to 24 | Tin | 43030-0001 | **43030-0007** |
| 26 to 30 | Tin | 43030-0004 | 43030-0010 |
| 20 to 24 | 15 microinch gold | 43030-0002 | 43030-0008 |
| 26 to 30 | 15 microinch gold | 43030-0005 | 43030-0011 |
| 20 to 24 | 30 microinch gold | 43030-0003 | 43030-0009 |
| 26 to 30 | 30 microinch gold | 43030-0006 | 43030-0012 |

Every one is 250 V, 5.0 A maximum, 10 milliohm maximum contact resistance, phosphor bronze. The
fitted 18 AWG [[430300038]] appears in none of them, consistent with this revision's table stopping
at 20 AWG.

## Consequence for the design, settled 2026-08-01

The design keeps **18 AWG into [[430300038]] on a single contact pair**, and accepts the 8.5 A that
distributors publish for that terminal as catalog evidence pending a current Molex revision.

**The comparison is RMS, not peak.** Molex's deratings are based on not exceeding a 30 degree
temperature rise, and contact heating is I squared R, so a 500 kHz inductor peak does not heat a
contact. The battery path is 4.442 A RMS. An earlier version of this page compared the 5.871 A peak
against a thermal rating and concluded the harness was 17 percent over; that was wrong.

The unresolved rating is not a blocker, because the harness passes under either candidate figure:
48 percent margin at 8.5 A, 11 percent at 5.0 A. What is open is the evidence class, not the
outcome. A current Molex revision would also supply the derating table for a fully energized
two-circuit housing, which this revision lacks.

A proposal to split the cell link across four contacts has been withdrawn. A single positive and
negative pair is the normal way to connect a cell; the multiple-contact wording in
`docs/hardware/power-module-interface.md` concerns the board-to-board links, where the connectors
already have spare pins; and paralleled contacts share current unevenly because their resistances
differ, so two are worth well under twice one.

## Related

- [[micro-fit-3-0-mating-evidence]]
- [[430300038]]
- [[430250200]]
