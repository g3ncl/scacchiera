---
type: index
date_updated: 2026-07-25
tags:
  - wiki/index
---



# Wiki Index

Content catalog for the wiki. Read this first before any query or ingest. Every
page the wiki owns is listed in one of the tables below. Raw clippings live in
[Clippings/](../Clippings) and are immutable, they are not listed here until
they have been ingested.

See [[overview]] for the high level synthesis and [[log]] for the operation history.

## Unprocessed sources

Raw sources that have been captured but not yet ingested into the wiki. Move a
row into the Sources table below once its summary page exists.

Component datasheets live in [Datasheets/](../Datasheets) and are immutable in the same way
`Clippings/` is. Every part the hardware binds should have one filed, with a `source-summary` here
and an `entity` page for the component; see the Datasheets section of `CLAUDE.md`. Filed so far:
ESP32-C6-MINI-1U, PN5180, TXC 7M27100009, SK6812MINI-E (rev 02), the SK68XX MINI family (rev 08),
the hub power tree and logic (MCP73871, TPS63802, TPS61023, TPS2553, TCA9535, SN74AHCT1G125,
USBLC6-2SC6) and the matrix discretes (BAR64-02V, BSS123, BSS84, 74HC595, SDFL2012S100KTF).
Still unfiled: the passives, the JST connectors, USB4105-GF-A, DMP2035U-7, BAT54H, MF-MSMF050-2,
JS102011SAQN, and the two RF inductors (DFE201610E, LQW2BASR47J00L).

Five further nfcgameboard.com pages are linked from the captured pages but not yet clipped:
`/why`, `/videos`, `/mechanics`, `/embedded`, `/presentation`. Not urgent: `/embedded` and
`/presentation` describe the author's Arduino/Windows implementation, which is downstream of the
concepts already captured from the white paper.

| Source | Captured | Notes |
| --- | --- | --- |
| _(none yet)_ | | |

## Sources

One [[wiki/source]] summary per ingested raw source. Factual, no interpretation.

| Page | Type | Updated |
| --- | --- | --- |
| [[nfcgameboard-home]] | nfcgameboard.com page | 2026-07-24 |
| [[nfcgameboard-schematics]] | nfcgameboard.com page | 2026-07-24 |
| [[nfcgameboard-pcb]] | nfcgameboard.com page | 2026-07-24 |
| [[nfcgameboard-software]] | nfcgameboard.com page | 2026-07-24 |
| [[bitwiseid-whitepaper]] | white paper (PDF, transcribed) | 2026-07-24 |
| [[jlcpcb-economic-parts-2026-07-24]] | economic-parts catalog snapshot | 2026-07-24 |
| [[jlcpcb-matrix-live-stock-2026-07-25]] | matrix live JLCPCB inventory | 2026-07-25 |
| [[schemalyzer-jlcpcb-design-rules-2025]] | third-party JLCPCB DFM guide | 2026-07-25 |
| [[esp32-c6-mini-1u-datasheet]] | component datasheet | 2026-07-25 |
| [[pn5180-crystal-and-clock-requirements]] | component datasheet (scoped extract) | 2026-07-25 |
| [[txc-7m27100009-datasheet]] | component datasheet | 2026-07-25 |
| [[sk68xx-mini-e-led-datasheets]] | component datasheets (two revisions, conflicting) | 2026-07-25 |
| [[hub-power-tree-datasheets]] | component datasheets (7 parts, power and logic) | 2026-07-25 |
| [[matrix-discrete-datasheets]] | component datasheets (5 parts, switch cell) | 2026-07-25 |

## Entities

People, tools, orgs, repos. See [[wiki/entity]] pages.

| Page | source_count | Updated |
| --- | --- | --- |
| [[ben-bulsink]] | 5 | 2026-07-24 |
| [[nfc-game-board-project]] | 4 | 2026-07-24 |
| [[clrc632]] | 2 | 2026-07-24 |
| [[jlcpcb]] | 3 | 2026-07-25 |
| [[esp32-c6-mini-1u]] | 2 | 2026-07-25 |
| [[pn5180]] | 2 | 2026-07-25 |
| [[txc-7m27100009]] | 2 | 2026-07-25 |
| [[sk6805mini-e]] | 1 | 2026-07-25 |

## Concepts

Ideas, patterns, techniques. See [[wiki/concept]] pages.

| Page                                    | Confidence | source_count | Updated    |
| --------------------------------------- | ---------- | ------------ | ---------- |
| [[bitwiseid-method]]                    | high       | 1            | 2026-07-24 |
| [[bitwisexy-method]]                    | high       | 1            | 2026-07-24 |
| [[set-management-and-setid]]            | high       | 1            | 2026-07-24 |
| [[row-column-antenna-matrix-technique]] | high       | 4            | 2026-07-24 |
| [[pin-diode-antenna-switching]]         | high       | 1            | 2026-07-24 |
| [[jlcpcb-basic-part-sourcing]]          | medium     | 3            | 2026-07-25 |
|                                         |            |              |            |

## Synthesis

Query answers filed back into the wiki. See [[wiki/synthesis]] pages.

| Page | Question | Updated |
| --- | --- | --- |
| [[tps2553-current-limit-error]] | 2 | high | 2026-07-25 |
| [[jlcpcb-matrix-bom-review]] | Make the matrix BOM stocked, exact, and assembly-safe | 2026-07-24 |
