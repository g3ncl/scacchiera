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
four matrix serial nets, its Q24 power escape, the hub USB shield tabs, recovery pads, and ground
stitching are deterministic code-owned geometry. Fresh autorouter output is available only through
explicit reroute targets and must be reviewed before replacing a passing session.

The gate checks both sides of the matrix and light-bar cables, every hub service connector, exact
USB-C pad identities, all enumerated no-connects, boot and power-off pulls, MCU reset and recovery,
and both IC exposed pads. Full KiCad PCB DRC runs with schematic parity. Each board reports zero
violations, zero unconnected items, and zero parity issues.

This result advances [[../../../docs/planning.md|the hardware plan]] through V2 only. Power and
fault corners, electromagnetic validation, firmware, fabrication preflight, measurements, and
independent review remain sequential gates.
