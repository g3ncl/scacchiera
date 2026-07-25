---
type: synthesis
date_updated: 2026-07-24
tags:
  - wiki/synthesis
---

# JLCPCB matrix BOM review

[question::How can the matrix BOM be made unambiguous, fully stocked, and electrically safe for
JLCPCB assembly?] [result::Fully bound, 11 BOM lines and 165 BOM/CPL references]

JLCPCB's first match exposed three separate problems: value-style BOM comments did not match the
selected manufacturer's MPN, five matched parts lacked inventory, and the PCB copper antenna loops
were offered as assembly components. The corrected export uses exact manufacturer numbers as
comments, binds every purchased line to an exact JLC code, and omits copper loops from both BOM and
CPL. The final reference sets are identical.

The unavailable BAP64-02 PIN diode was replaced by JSCJ BAR64-02V, C5295579. Its SOD-523 package,
polarity, reverse-voltage rating, forward RF resistance, and reverse capacitance satisfy the switch
cell. A conservative model using the replacement's maximum RF values passes the matrix criteria:
14.179 MHz cell resonance, 13.385 MHz loaded-bus resonance, 84.6 dB suppression, and 10.29 mA bias.
This is a validated substitution, not a catalog-name guess.

The fee review also replaced the Extended TI TSSOP shift registers with Basic Nexperia
74HC595D,118, C5947. The SOIC-16 package is larger but preserves the standard pinout, supply range,
logic function, and active-low controls while removing one unique Extended BOM line.

The final sourcing table, stock evidence, cost comparison, and exact part numbers live in
[[../../../docs/hardware/jlcpcb-sourcing.md|the JLCPCB sourcing register]]. The general rule remains
[[jlcpcb-basic-part-sourcing]]: the JLC code and exact MPN must identify the same device, while the
engineering value stays in the internal BOM.

## Related

- [[jlcpcb]]
- [[pin-diode-antenna-switching]]
- [[jlcpcb-economic-parts-2026-07-24]]
