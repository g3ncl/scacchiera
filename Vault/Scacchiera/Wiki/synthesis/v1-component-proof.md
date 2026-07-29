---
type: synthesis
tags:
  - wiki/synthesis
  - wiki/verification
date_updated: 2026-07-30
---

# V1 component proof

How is every fitted component tied to an exact purchasable part, authoritative source, library
audit and simulation treatment?

The four authoritative schematics generate 58 unique purchased fitted MPN, supplier, order-code and
footprint tuples with no fitted sourcing blocker.
`docs/verification/v1-components.yaml` records each exact tuple, and the generated
catalogs in [[index]] link one source summary and one entity page per exact MPN. The test suite
rebuilds the inventory from SKiDL and requires exact set equality, so changing a fitted part without
updating its evidence fails V1.

The same evidence separately binds the external [[ntcle317e4103sba]] cell sensor: its interface,
ratings, immutable sources, availability and simulation treatment are checked without pretending an
off-board item has a PCB footprint.

**V1 remains open on the display and battery assemblies as of 2026-07-29.** The custom power board
binds [[bq25895rtwr]], [[tps61088rhlr]], [[csd25404q3]], [[tlv7021dckr]], both Micro-Fit headers,
exact [[dfe252012f-1r0m-p2]], LCSC C435392, and [[0402b223k500nt]], Basic C1532. The
[[er-oledm3-12-1w-manufacturer-evidence]] capture records a conflict between 320 mA active current
in the datasheet and 2 mA on the product page, while the original PDF and exact 16-to-7-pin cable
remain unfiled. A purchased power-module replacement is optional and therefore not a fitted V1 item.

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

The rebuilt hub removed the charger and duplicate conversion stages from the hub itself. Its
[[ap63203wu-7-datasheet]], [[ap22811aw5-7-datasheet]], [[tlv7042dgkr-datasheet]], and
[[nr6045s4r7mt-datasheet]] records include the exact limits used by the design. The rejected
[[swpa5045s4r7mt-datasheet]] remains visible because the manufacturer table does not substantiate
the catalog MPN. The comparator uses a code-generated DGK0008A manufacturer land pattern after PCB
DRC showed the generic KiCad VSSOP footprint could not maintain the board's 0.2 mm clearance.

[component_count::58] [blocked_fitted_component_count::0] [external_component_count::2]
[gate_state::open, display documentation conflict and interconnect]
[vendor_model_count::3]

Related: [[verification-evidence-model]], [[jlcpcb]], [[matrix-discrete-datasheets]]
