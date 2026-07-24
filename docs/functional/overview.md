# Functional specification

This directory is the product functional specification: what the connected chessboard is and must do,
independent of how the pieces are sensed. It is the stable set of requirements the hardware and
software implementations serve, so it survives a change of sensing architecture (the move from 64
local antennas to the 8+8 row-column matrix, and anything after it). Anything tied to a specific
antenna count, reader, tag type, or PCB topology lives in the implementation docs under `hardware/`
and `software/`, not here.

## Principles

- The physical typed position is authoritative. The board never infers a move from history; a
  sensing fault is reported, never converted into a legal move.
- The board is fully usable with no connected browser. A browser client only mirrors state and
  configures the board.
- It is a standard 8x8 chessboard: 64 squares, standard rules, standard results.

## Fixed here vs decided in implementation

Fixed by this directory (stable requirements):

- gameplay and rules behavior, clock and results;
- fault detection and recovery semantics;
- piece provisioning behavior;
- physical form factor and dimensions;
- the tag-to-surface read budget;
- the display, light-bar, and button interface.

Decided in the implementation docs, not here (may change without touching this directory):

- how a square's occupant is identified (sensing architecture, antenna geometry, switching);
- the NFC tag type and the reader;
- PCB topology and layout;
- power and thermal budgets.

## Contents

- [overview.md](overview.md): this page.
- [gameplay.md](gameplay.md): game flow, clock, results, faults, provisioning, and the browser client.
- [physical.md](physical.md): board geometry, the playing surface, and the piece/tag read budget.
- [interface.md](interface.md): the two displays, the light bars, the button, and feedback semantics.
