---
type: entity
date_updated: 2026-07-25
source_count: 3
tags:
  - wiki/entity
---

# JLCPCB

[kind::PCB fabrication and assembly service] [parts_supplier::LCSC]

The assembly service targeted by the chessboard's fabrication output. It consumes a Gerber archive,
a BOM containing LCSC part numbers, and a CPL with `Designator`, `Mid X`, `Mid Y`, `Rotation`, and
`Layer` columns. Its current economic-parts snapshot supports conservative sourcing decisions in
[[jlcpcb-basic-part-sourcing]].

## Sources

- [[jlcpcb-economic-parts-2026-07-24]]
- [[jlcpcb-matrix-live-stock-2026-07-25]]
- [[schemalyzer-jlcpcb-design-rules-2025]]
