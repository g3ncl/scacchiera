# Smart Chessboard documentation

This directory holds the specification for the connected chessboard.

## Documents

- [Functional specification](functional/overview.md): what the board is and must do (gameplay, physical form, and interface), independent of any sensing architecture or other implementation choice. This is the stable requirement set all hardware and software design serves.
- [Hardware development plan](planning.md): the milestone list hardware development follows, from board inventory through schematic, PCB layout, and SPICE validation.

## Current state

The rebuild is well underway; see [planning.md](planning.md) for milestone status. The board
inventory ([hardware/boards.md](hardware/boards.md)) defines three custom designs: the light bar
([hardware/lightbar.md](hardware/lightbar.md), fully done), the sensing matrix board
([hardware/matrix.md](hardware/matrix.md)), and the hub ([hardware/hub.md](hardware/hub.md)).
All three schematics are ERC-clean with costed BOMs, all three have passing ngspice validations
against [hardware/criteria.yaml](hardware/criteria.yaml) in the ordinary test suite, and all
three PCB layouts are generated from code and DRC-clean (0 violations, 0 unconnected). Every
board has cleared its milestones, so the hardware rebuild is complete. Firmware and the companion
app have not started.

[JLCPCB assembly sourcing](hardware/jlcpcb-sourcing.md) records the Basic-part selections,
unresolved assembly items, and the cost-review rule for any replacement IC.

Both the functional spec and the future implementation draw on the [Obsidian vault](../Vault/Scacchiera/) at the repository root, which holds the external research feeding the chessboard (reference projects, papers, datasheets) as an LLM-maintained wiki over immutable raw captures. Start at [Vault/Scacchiera/Wiki/index.md](../Vault/Scacchiera/Wiki/index.md); see `CLAUDE.md` for how it is maintained.
