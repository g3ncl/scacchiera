---
type: synthesis
date_updated: 2026-07-26
tags:
  - wiki/synthesis
---

# V2 static connectivity proof

V2 closes the gap between an electrically plausible schematic and a reproducible routed board.
The authoritative evidence is
[[../../../../docs/verification/v2-static.yaml|docs/verification/v2-static.yaml]], backed by the exact
component sources already cataloged in [[index]].

The repair found real connectivity defects. The hub's earlier generic USB symbol did not model the
USB4105's alphanumeric pads or repeated shield tabs, the TPS63802 and PN5180 exposed pads were absent
from their symbols, and plated mounting holes existed only on the PCB side. The matrix router also
owned serial-register escape nets that it completed differently between runs. These were corrected
in the schematics and generation code, not waived in reports.

Normal matrix and hub builds now import reviewed Specctra sessions from versioned route files. The
four matrix serial nets, its Q24 power escape, the hub USB shield tabs, and its 0.5 mm VBUS
distribution and reference branch are deterministic code-owned geometry. Fresh autorouter output is
available only through explicit reroute targets and must be reviewed before replacing a passing
session.

Every board is two copper layers. The hub spent a day at four, after a 110 x 46 mm two-layer route
repeatedly stranded different long nets, and returned to two by growing to 162 x 46 mm: the service
volume is a 310 mm player rail holding only that board, so length is the cheap dimension and layers
are not. The comparator branch and SCLK bridge that four layers had needed were removed rather than
pushed onto the back copper, where they would have cut the return path they were meant to protect.

The gate checks both sides of the matrix and light-bar cables, every hub service connector, exact
USB-C pad identities, all enumerated no-connects, boot and power-off pulls, MCU reset and recovery,
and both IC exposed pads. Full KiCad PCB DRC runs with schematic parity. Each board reports zero
violations, zero unconnected items, and zero parity issues.

The rebuilt hub result is reproducible through `make pcb-hub-drc`. Seven focused static tests pass,
including the power-module boundary, the independent hardware temperature gate, the on-board battery
measurement, and the recorded stackup and envelope.

On two layers the back copper is both the ground return and the router's second routing layer, so
the region under the reader's match and the run to the matrix connector is reserved: no tracks, vias
allowed, and zero signal segments measured inside it. The reserve stops short of the reader, because
a QFN-40 in a 6 mm body needs both faces to escape its own pins.

A layer count is not free downstream. The fabrication export used to name its Gerber layers as a
fixed outer pair, which would have shipped the four-layer hub missing both inner layers and the
copper its route depended on. The export now reads the copper stack from the board itself, so the
question stopped mattering when the board went back to two layers, which is the point of deriving it
rather than declaring it. The recorded stackup and envelope are asserted against the generated board
rather than described only in prose. [layer-count::2] [envelope_mm::162 x 46]
[gerber_layers::derived from the board]

This result advances [[../../../../docs/planning.md|the hardware plan]] through V2 only. Power and
fault corners, electromagnetic validation, firmware, fabrication preflight, measurements, and
independent review remain sequential gates.
