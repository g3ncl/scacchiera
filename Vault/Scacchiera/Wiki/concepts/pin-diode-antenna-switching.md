---
type: concept
date_updated: 2026-07-24
source_count: 1
confidence: high
tags:
  - wiki/concept
---

# PIN diode antenna switching

[origin::[[nfc-game-board-project]], independently rediscovered in our own design] [used_by::[[nfc-game-board-project]]]

Use series PIN diodes, not general-purpose analog switch ICs, to select one antenna out of many
on a shared HF bus. Per [[nfcgameboard-schematics]], the author tried analog switch ICs first and
rejected them: even "quite expensive" ones show enough off-state capacitance that paralleling 30
of them (the board's row+column count) sums to roughly 300 pF, far too much for a 13.56 MHz tank.
A PIN diode shows **sub-pF capacitance in reverse (off) bias**, which keeps the shared bus in
budget; the NFC Game Board project drives its diodes from a 5V-to-24V DC converter, since higher
reverse bias voltage gives lower capacitance and higher forward bias current gives lower forward
resistance.

## Independent convergence

An earlier iteration of our own hardware design reached the identical conclusion by direct SPICE
simulation of a 64-antenna shared bus: a pure-MOSFET switch (BSS123, ~5 pF off-capacitance)
collapses the selected resonance from ~13.8 MHz (1 cell) to an extrapolated ~4.8 MHz (64 cells),
while PIN diodes (BAP64-02, ~0.3 pF) keep the bus in the 12.5-15 MHz acceptance band even fully
loaded (measured 13.7 MHz at 64 cells). That implementation has since been discarded for a
from-scratch rebuild (see [[../../../docs/planning.md|docs/planning.md]]); the rebuilt matrix
board re-adopted the technique, as a single-ended half of the old hybrid cell (one series
BAP64-02 plus a shunt BSS123 per line, validated again in ngspice, see `docs/hardware/matrix.md`).
The simulation result is kept here as reference data: PIN-diode RF
switching is long-established prior art with no patent risk (the technique the NFC Gameboard author
referenced patenting is orthogonal coding for a row-column matrix, i.e.
[[bitwiseid-method|BitwiseID]] itself, not the diode switching).

## Sources

- [[nfcgameboard-schematics]]

## Related

- [[nfc-game-board-project]]
- [[row-column-antenna-matrix-technique]]
- [[clrc632]]
