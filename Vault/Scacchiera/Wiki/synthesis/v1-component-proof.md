---
type: synthesis
tags:
  - wiki/synthesis
  - wiki/verification
date_updated: 2026-07-25
---

# V1 component proof

How is every fitted component tied to an exact purchasable part, authoritative source, library
audit and simulation treatment?

The authoritative schematics generate 59 unique purchased fitted MPN, supplier, order-code and
footprint tuples. `docs/verification/v1-components.yaml` records each tuple and the generated
catalogs in [[index]] link one source summary and one entity page per exact MPN. The test suite
rebuilds the inventory from SKiDL and requires exact set equality, so changing a fitted part without
updating its evidence fails V1.

Three ambiguities were resolved by changing parts. The rejected SK6805 selection is preserved in
[[sk6805mini-e]], while the fitted lightbar source is now [[t37k3rgb-05c000112u1930-datasheet]].
The matrix's generic BSS selections were replaced by exact Diodes Incorporated orderable parts,
[[bss123-7-f-datasheet]] and [[bss84-7-f-datasheet]], and their vendor SPICE models are the ones
used by the RF tests. The exact ESP32 module and Würth inductor have stocked DigiKey cut-tape
fallbacks rather than relying on unpublished JLC quantities.

The Samsung files served through the catalog were environmental declarations rather than component
specifications. They remain immutable raw evidence of the mismatch. Each fitted Samsung part points
instead to the separately filed official manufacturer specification whose filename ends in
`_manufacturer.pdf`. Automated checks reject a Samsung V1 record that points to the wrong file.

[component_count::59] [open_conflict_count::0] [vendor_model_count::5]

Related: [[verification-evidence-model]], [[jlcpcb]], [[matrix-discrete-datasheets]]
