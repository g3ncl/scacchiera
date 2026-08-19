# Smart Chessboard documentation

This directory holds the specification for the connected chessboard.

## Where to start

- [Functional specification](functional/overview.md): what the board is and must do (gameplay,
  physical form, interface, power), independent of any sensing architecture. This is the stable
  requirement set every hardware and software decision serves.
- [Simulation and verification workflow](simulation-workflow.md): the V0 to V9 evidence gates. No
  board may be called done, and no fabrication order released, until its gate passes.
- [Hardware development plan](planning.md): current gate status and the milestone list development
  follows.

## Current state

The board inventory ([hardware/boards.md](hardware/boards.md)) is four custom designs in eight
physical PCBs: the light bar (x2), [the four-lane sensing board](hardware/quad.md) (x4), the hub,
and the power board. The sensing plane was settled on 2026-08-02 in favour of the four-lane split;
the monolithic [matrix board](hardware/matrix.md) is retained as the measured baseline it was
chosen against, not as a shipping option.

| Area | State |
| --- | --- |
| Schematics | Five designs generate, ERC clean, each with a costed BOM |
| Layouts | Five designs routed from code, DRC and schematic parity clean |
| Verification | V0 and V2 pass. V1, V3, V4, V5 and V7 are partly evidenced. V6, V8 and V9 have not started |
| Firmware | Host test gate and ESP32-C6 target image both build; six drivers exist; the rules engine is a stub |
| Companion app | Not started |

Nothing is authorised for fabrication. The nearest releasable item is the scoped
[bare sensing-plane test article](hardware/test-article-quad.md), which is still gated on the open
V3, V4 and V7 items in [planning.md](planning.md).

## Hardware reference

| Document | Covers |
| --- | --- |
| [boards.md](hardware/boards.md) | The board split, what each board owns, and the purchased accessories on no BOM |
| [quad.md](hardware/quad.md) | The shipping sensing plane: four lanes per board, four boards |
| [matrix.md](hardware/matrix.md) | The superseded monolith, retained as the antenna and tag baseline |
| [hub.md](hardware/hub.md) | Controller, reader front end, rails and every harness connector |
| [power.md](hardware/power.md) | Charger, reverse-cell protection and the 5 V at 2 A output stage |
| [lightbar.md](hardware/lightbar.md) | The 14-pixel player feedback bar |
| [criteria.yaml](hardware/criteria.yaml) | Every numeric pass limit with its evidence class and margin |
| [assumptions.md](hardware/assumptions.md) | The eleven values carried without a datasheet behind them |

Interfaces and purchased items get their own contracts:
[display-interface.md](hardware/display-interface.md),
[power-module-interface.md](hardware/power-module-interface.md),
[cell-assembly.md](hardware/cell-assembly.md), and [harnesses.md](hardware/harnesses.md).

## Cost and ordering

[Electronics cost](hardware/cost.md) totals one complete board and ranks the remaining savings; its
headline is that no single component dominates and per-order fixed cost does.
[JLCPCB sourcing](hardware/jlcpcb-sourcing.md) records the part selections, the assembly route per
board, and the items needing follow-up. [Ordering](hardware/ordering.md) says which generated file
to upload for which quote, and which ones never to upload. Getting a price is not ordering.

## Research

Both the functional spec and the implementation draw on the [Obsidian vault](../Vault/Scacchiera/)
at the repository root, which holds the external research feeding the chessboard (reference
projects, papers, datasheets) as an LLM-maintained wiki over immutable raw captures. Start at
[Vault/Scacchiera/Wiki/index.md](../Vault/Scacchiera/Wiki/index.md); see `CLAUDE.md` for how it is
maintained.
