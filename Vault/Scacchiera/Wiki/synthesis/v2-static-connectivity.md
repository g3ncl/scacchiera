---
type: synthesis
date_updated: 2026-07-26
tags:
  - wiki/synthesis
---

# V2 static connectivity proof

V2 closes the gap between an electrically plausible schematic and a reproducible routed board.
The authoritative evidence is
[[../../../docs/verification/v2-static.yaml|docs/verification/v2-static.yaml]], backed by the exact
component sources already cataloged in [[index]].

The repair found real connectivity defects. The hub's earlier generic USB symbol did not model the
USB4105's alphanumeric pads or repeated shield tabs, the TPS63802 and PN5180 exposed pads were absent
from their symbols, and plated mounting holes existed only on the PCB side. The matrix router also
owned serial-register escape nets that it completed differently between runs. These were corrected
in the schematics and generation code, not waived in reports.

Normal matrix and hub builds now import reviewed Specctra sessions from versioned route files. The
four matrix serial nets, its Q24 power escape, the hub USB shield tabs, 0.5 mm VBUS distribution,
comparator supply branch, reader SCLK, recovery pads, and ground stitching are deterministic
code-owned geometry. The 110 x 46 mm hub uses four copper layers because repeated two-layer trials
stranded different long nets and fragmented the return around the MCU and NFC front end. Only the
matrix is functionally constrained to two layers. Fresh autorouter output is available only through
explicit reroute targets and must be reviewed before replacing a passing session.

The gate checks both sides of the matrix and light-bar cables, every hub service connector, exact
USB-C pad identities, all enumerated no-connects, boot and power-off pulls, MCU reset and recovery,
and both IC exposed pads. Full KiCad PCB DRC runs with schematic parity. Each board reports zero
violations, zero unconnected items, and zero parity issues.

The rebuilt hub result is reproducible through `make pcb-hub-drc`. Six focused static tests pass,
including the commercial power boundary and independent hardware temperature gate.

A layer count is not free downstream. The fabrication export previously named its Gerber layers as a
fixed outer pair, which would have shipped a hub package missing both inner layers, including the
inner-copper VBUS and SCLK branches the route depends on. The export now reads the copper stack from
the board itself, and the recorded stackup is asserted against the generated board rather than
described only in prose. [layer-count::4] [gerber_layers::derived from the board]

This result advances [[../../../docs/planning.md|the hardware plan]] through V2 only. Power and
fault corners, electromagnetic validation, firmware, fabrication preflight, measurements, and
independent review remain sequential gates.
