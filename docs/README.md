# Smart Chessboard documentation

This directory holds the specification for the connected chessboard.

## Documents

- [Functional specification](functional/overview.md): what the board is and must do (gameplay, physical form, and interface), independent of any sensing architecture or other implementation choice. This is the stable requirement set all hardware and software design serves.
- [Hardware development plan](planning.md): the milestone list hardware development follows, from board inventory through schematic, PCB layout, and SPICE validation.

## Current state

The rebuild is well underway; see [planning.md](planning.md) for milestone status. The board
inventory ([hardware/boards.md](hardware/boards.md)) defines four custom designs: the light bar,
the sensing matrix, the hub and the power board. A further design,
[the four-lane sensing board](hardware/quad.md), is an alternative way of cutting the sensing plane
rather than an addition to the product; exactly one of the two sensing architectures ships. All
five schematics and code-generated layouts pass the current ERC, DRC and schematic-parity gates. Simulation coverage is partial, and the new
power board has no V3 corner or fault simulation yet, and its boost converter must change after the
display datasheet raised coincident load to 1.48 A. V1 is open on the display documentation conflict
and exact cable definition; every fitted custom-board part is sourced. Firmware and the companion
app have not started. No board is authorized for fabrication until the release gates in
[simulation-workflow.md](simulation-workflow.md) pass.

[JLCPCB assembly sourcing](hardware/jlcpcb-sourcing.md) records the Basic-part selections,
unresolved assembly items, and the cost-review rule for any replacement IC.

Both the functional spec and the future implementation draw on the [Obsidian vault](../Vault/Scacchiera/) at the repository root, which holds the external research feeding the chessboard (reference projects, papers, datasheets) as an LLM-maintained wiki over immutable raw captures. Start at [Vault/Scacchiera/Wiki/index.md](../Vault/Scacchiera/Wiki/index.md); see `CLAUDE.md` for how it is maintained.
