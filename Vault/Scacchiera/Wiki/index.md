---
type: index
date_updated: 2026-08-02
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
`Clippings/` is. V1 filed and ingested all 54 purchased fitted MPNs plus two external electrical
components. The generated catalogs below list one `source-summary` and one component `entity` per
exact fitted part. Historical family summaries
remain because they explain rejected selections and contradictions that must not be forgotten.

Five further nfcgameboard.com pages are linked from the captured pages but not yet clipped:
`/why`, `/videos`, `/mechanics`, `/embedded`, `/presentation`. Not urgent: `/embedded` and
`/presentation` describe the author's Arduino/Windows implementation, which is downstream of the
concepts already captured from the white paper.

| Source | Captured | Notes |
| --- | --- | --- |
| _(none yet)_ | | |

## Sources

One `wiki/source` summary per ingested raw source. Factual, no interpretation.

| Page | Type | Updated |
| --- | --- | --- |
| [[nfcgameboard-home]] | nfcgameboard.com page | 2026-07-24 |
| [[nfcgameboard-schematics]] | nfcgameboard.com page | 2026-07-24 |
| [[nfcgameboard-pcb]] | nfcgameboard.com page | 2026-07-24 |
| [[nfcgameboard-software]] | nfcgameboard.com page | 2026-07-24 |
| [[bitwiseid-whitepaper]] | white paper (PDF, transcribed) | 2026-07-24 |
| [[jlcpcb-economic-parts-2026-07-24]] | economic-parts catalog snapshot | 2026-07-24 |
| [[jlcpcb-economic-parts-2026-08-02]] | economic-parts catalog snapshot (fee-free subset, 1586 live parts) | 2026-08-02 |
| [[jlcpcb-matrix-live-stock-2026-07-25]] | matrix live JLCPCB inventory | 2026-07-25 |
| [[schemalyzer-jlcpcb-design-rules-2025]] | third-party JLCPCB DFM guide | 2026-07-25 |
| [[esp32-c6-mini-1u-datasheet]] | component datasheet | 2026-07-25 |
| [[pn5180-crystal-and-clock-requirements]] | component datasheet (scoped extract) | 2026-07-25 |
| [[txc-7m27100009-datasheet]] | component datasheet | 2026-07-25 |
| [[sk68xx-mini-e-led-datasheets]] | component datasheets (two revisions, conflicting) | 2026-07-25 |
| [[hub-power-tree-datasheets]] | component datasheets (7 parts, power and logic) | 2026-07-25 |
| [[matrix-discrete-datasheets]] | component datasheets (5 parts, switch cell) | 2026-07-25 |
| [[inr-21700-m65a-datasheet]] | component datasheet | 2026-07-30 |
| [[bq25638-datasheet]] | component datasheet | 2026-07-26 |
| [[tps25730-datasheet]] | component datasheet | 2026-07-26 |
| [[pmp23456-reference-design]] | TI reference-design test report | 2026-07-26 |
| [[sw6106-datasheet]] | component datasheet | 2026-07-26 |
| [[rbs18634-datasheet]] | module product sheet | 2026-07-26 |
| [[pisugar3-plus-manufacturer-docs]] | commercial UPS manufacturer documentation | 2026-07-26 |
| [[955465-un38-3]] | battery UN 38.3 test report | 2026-07-26 |
| [[ntcle317e4103sba-datasheet]] | component datasheet | 2026-07-26 |
| [[ntcle317e4103sba-rt-curve]] | manufacturer resistance curve | 2026-07-26 |
| [[swpa5045s4r7mt-datasheet]] | component datasheet | 2026-07-26 |
| [[er-oledm3-12-1w-manufacturer-evidence]] | component manufacturer evidence | 2026-08-01 |
| [[bq25619rtwr-datasheet]] | component datasheet | 2026-07-29 |
| [[bq25895rtwr-datasheet]] | component datasheet | 2026-07-31 |
| [[tps61088rhlr-datasheet]] | component datasheet | 2026-08-19 |
| [[micro-fit-3-0-mating-evidence]] | connector manufacturer evidence | 2026-07-29 |
| [[usb-type-c-r2-current-advertisement]] | USB Type-C specification scoped extract | 2026-07-29 |
| [[ssd1362-datasheet]] | component datasheet | 2026-07-30 |
| [[sl2s2602-datasheet]] | component datasheet (piece tag IC, off-board) | 2026-08-01 |
| [[ad-circus-slix2-datasheet]] | inlay product data sheet (piece tag, off-board) | 2026-08-01 |
| [[w256064-xalg-datasheet]] | comparable panel datasheet (corroborating, not fitted) | 2026-08-01 |
| [[micro-fit-current-rating]] | connector product specification (mirror, revision superseded) | 2026-08-01 |

## Entities

People, tools, orgs, repos. See `wiki/entity` pages.

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
| [[inr-21700-m65a]] | 1 | 2026-07-30 |
| [[bq25638]] | 2 | 2026-07-26 |
| [[tps25730s]] | 2 | 2026-07-26 |
| [[sw6106]] | 2 | 2026-07-26 |
| [[rbs18634]] | 2 | 2026-07-26 |
| [[pisugar3-plus]] | 2 | 2026-07-26 |
| [[tlv7042]] | 1 | 2026-07-26 |
| [[ntcle317e4103sba]] | 1 | 2026-07-26 |
| [[swpa5045s4r7mt]] | 1 | 2026-07-26 |
| [[er-oledm3-12-1w]] | 2 | 2026-07-30 |
| [[ssd1362]] | 1 | 2026-07-30 |
| [[bq25619rtwr]] | 1 | 2026-07-29 |
| [[bq25895rtwr]] | 1 | 2026-07-29 |
| [[tps61088rhlr]] | 1 | 2026-07-29 |
| [[430250800]] | 1 | 2026-07-29 |
| [[430250200]] | 1 | 2026-07-29 |
| [[430300038]] | 1 | 2026-07-29 |
| [[sl2s2602]] | 1 | 2026-08-01 |
| [[ad-circus-slix2]] | 1 | 2026-08-01 |

<!-- V1-COMPONENT-CATALOG:START -->
## V1 component datasheet sources

One exact source summary per purchased fitted MPN. The structured audit is
`docs/verification/v1-components.yaml`.

| Page | Manufacturer | Updated |
| --- | --- | --- |
| [[0402b223k500nt-datasheet]] | Fenghua Advanced Technology | 2026-07-29 |
| [[0402cg101j500nt-datasheet]] | Fenghua Advanced Technology | 2026-07-26 |
| [[0402cg150j500nt-datasheet]] | Fenghua Advanced Technology | 2026-07-26 |
| [[0603waf1000t5e-datasheet]] | UNI-ROYAL | 2026-07-29 |
| [[0603waf1001t5e-datasheet]] | UNI-ROYAL | 2026-07-26 |
| [[0603waf1002t5e-datasheet]] | UNI-ROYAL | 2026-07-29 |
| [[0603waf1003t5e-datasheet]] | UNI-ROYAL | 2026-07-29 |
| [[0603waf1004t5e-datasheet]] | UNI-ROYAL | 2026-07-29 |
| [[0603waf150kt5e-datasheet]] | UNI-ROYAL | 2026-07-26 |
| [[0603waf2492t5e-datasheet]] | UNI-ROYAL | 2026-07-29 |
| [[0603waf3902t5e-datasheet]] | UNI-ROYAL | 2026-07-29 |
| [[0603waf4701t5e-datasheet]] | UNI-ROYAL | 2026-07-26 |
| [[0603waf5101t5e-datasheet]] | UNI-ROYAL | 2026-07-29 |
| [[0603waf9102t5e-datasheet]] | UNI-ROYAL | 2026-07-29 |
| [[430450200-datasheet]] | Molex | 2026-07-29 |
| [[430450800-datasheet]] | Molex | 2026-07-29 |
| [[74hc595d-118-datasheet]] | Nexperia | 2026-07-26 |
| [[7m27100009-datasheet]] | TXC | 2026-07-26 |
| [[a1257wr-s-4p-datasheet]] | CJT | 2026-07-26 |
| [[ap22811aw5-7-datasheet]] | Diodes Incorporated | 2026-08-19 |
| [[ap63203wu-7-datasheet]] | Diodes Incorporated | 2026-08-19 |
| [[bar64-02v-datasheet]] | Jiangsu Changjing Electronics Technology | 2026-07-26 |
| [[bat54h-datasheet]] | Jiangsu Changjing Electronics Technology | 2026-07-29 |
| [[bq25895rtwr-datasheet]] | Texas Instruments | 2026-07-31 |
| [[bss123-7-f-datasheet]] | Diodes Incorporated | 2026-07-26 |
| [[bss84-7-f-datasheet]] | Diodes Incorporated | 2026-07-26 |
| [[cc0603frnpo9bn221-datasheet]] | Yageo | 2026-07-26 |
| [[cc1206kkx7rcbb472-datasheet]] | Yageo | 2026-07-26 |
| [[cdmc8d28np-1r2mc-datasheet]] | Sumida | 2026-08-01 |
| [[cl05a105ka5nqnc-datasheet]] | Samsung Electro-Mechanics | 2026-07-26 |
| [[cl05b104ko5nnnc-datasheet]] | Samsung Electro-Mechanics | 2026-07-29 |
| [[cl10a105kb8nnnc-datasheet]] | Samsung Electro-Mechanics | 2026-07-29 |
| [[cl10a225ko8nnnc-datasheet]] | Samsung Electro-Mechanics | 2026-07-29 |
| [[cl21a106kaynnne-datasheet]] | Samsung Electro-Mechanics | 2026-07-29 |
| [[cl21a226maqnnne-datasheet]] | Samsung Electro-Mechanics | 2026-07-29 |
| [[cl21a475kaqnnne-datasheet]] | Samsung Electro-Mechanics | 2026-07-29 |
| [[cl32a107mqvnnne-datasheet]] | Samsung Electro-Mechanics | 2026-07-26 |
| [[csd25404q3-datasheet]] | Texas Instruments | 2026-07-31 |
| [[dfe252012f-1r0m-p2-datasheet]] | Murata | 2026-07-29 |
| [[esp32-c6-mini-1u-n4-datasheet]] | Espressif Systems | 2026-07-26 |
| [[grm1555c1h221ja01d-datasheet]] | Murata | 2026-07-26 |
| [[grm1555c1h680ja01d-datasheet]] | Murata | 2026-07-26 |
| [[lqm21dh100m70l-datasheet]] | Murata | 2026-08-20 |
| [[lqw2basr47j00l-datasheet]] | Murata | 2026-07-26 |
| [[nr6045s4r7mt-datasheet]] | Magnetsyc | 2026-08-01 |
| [[pn5180a0hn-c3e-datasheet]] | NXP Semiconductors | 2026-08-18 |
| [[rs-03k1800ft-datasheet]] | Fenghua Advanced Technology | 2026-07-26 |
| [[sdfl2012s100ktf-datasheet]] | Sunlord | 2026-07-26 |
| [[sm02b-ghs-tb-lf-sn-datasheet]] | JST | 2026-07-26 |
| [[sm07b-ghs-tb-lf-sn-datasheet]] | JST | 2026-07-29 |
| [[sn74ahct1g125dbvr-datasheet]] | Texas Instruments | 2026-08-01 |
| [[t37k3rgb-05c000112u1930-datasheet]] | Harvatek | 2026-07-26 |
| [[tca9535pwr-datasheet]] | Texas Instruments | 2026-07-31 |
| [[tlv7021dckr-datasheet]] | Texas Instruments | 2026-08-20 |
| [[tlv7042dgkr-datasheet]] | Texas Instruments | 2026-07-26 |
| [[tlv809k33dbvr-datasheet]] | Texas Instruments | 2026-07-29 |
| [[tps2553dbvr-1-datasheet]] | Texas Instruments | 2026-08-01 |
| [[tps61088rhlr-datasheet]] | Texas Instruments | 2026-07-31 |
| [[usb4105-gf-a-datasheet]] | GCT | 2026-07-26 |

## V1 component entities

| Page | source_count | Updated |
| --- | ---: | --- |
| [[0402b223k500nt]] | 1 | 2026-07-29 |
| [[0402cg101j500nt]] | 1 | 2026-07-26 |
| [[0402cg150j500nt]] | 1 | 2026-07-26 |
| [[0603waf1000t5e]] | 1 | 2026-07-29 |
| [[0603waf1001t5e]] | 1 | 2026-07-26 |
| [[0603waf1002t5e]] | 1 | 2026-07-29 |
| [[0603waf1003t5e]] | 1 | 2026-07-29 |
| [[0603waf1004t5e]] | 1 | 2026-07-29 |
| [[0603waf150kt5e]] | 1 | 2026-07-26 |
| [[0603waf2492t5e]] | 1 | 2026-07-29 |
| [[0603waf3902t5e]] | 1 | 2026-07-29 |
| [[0603waf4701t5e]] | 1 | 2026-07-26 |
| [[0603waf5101t5e]] | 1 | 2026-07-29 |
| [[0603waf9102t5e]] | 1 | 2026-07-29 |
| [[430450200]] | 1 | 2026-07-29 |
| [[430450800]] | 1 | 2026-07-29 |
| [[74hc595d-118]] | 1 | 2026-07-26 |
| [[7m27100009]] | 1 | 2026-07-26 |
| [[a1257wr-s-4p]] | 1 | 2026-07-26 |
| [[ap22811aw5-7]] | 1 | 2026-07-26 |
| [[ap63203wu-7]] | 1 | 2026-07-26 |
| [[bar64-02v]] | 1 | 2026-07-26 |
| [[bat54h]] | 1 | 2026-07-29 |
| [[bq25895rtwr]] | 1 | 2026-07-29 |
| [[bss123-7-f]] | 1 | 2026-07-26 |
| [[bss84-7-f]] | 1 | 2026-07-26 |
| [[cc0603frnpo9bn221]] | 1 | 2026-07-26 |
| [[cc1206kkx7rcbb472]] | 1 | 2026-07-26 |
| [[cdmc8d28np-1r2mc]] | 1 | 2026-07-29 |
| [[cl05a105ka5nqnc]] | 1 | 2026-07-26 |
| [[cl05b104ko5nnnc]] | 1 | 2026-07-29 |
| [[cl10a105kb8nnnc]] | 1 | 2026-07-29 |
| [[cl10a225ko8nnnc]] | 1 | 2026-07-29 |
| [[cl21a106kaynnne]] | 1 | 2026-07-29 |
| [[cl21a226maqnnne]] | 1 | 2026-07-29 |
| [[cl21a475kaqnnne]] | 1 | 2026-07-29 |
| [[cl32a107mqvnnne]] | 1 | 2026-07-26 |
| [[csd25404q3]] | 1 | 2026-07-29 |
| [[dfe252012f-1r0m-p2]] | 1 | 2026-07-29 |
| [[esp32-c6-mini-1u-n4]] | 1 | 2026-07-26 |
| [[grm1555c1h221ja01d]] | 1 | 2026-07-26 |
| [[grm1555c1h680ja01d]] | 1 | 2026-07-26 |
| [[lqm21dh100m70l]] | 1 | 2026-08-20 |
| [[lqw2basr47j00l]] | 1 | 2026-07-26 |
| [[nr6045s4r7mt]] | 1 | 2026-07-29 |
| [[pn5180a0hn-c3e]] | 1 | 2026-07-26 |
| [[rs-03k1800ft]] | 1 | 2026-07-26 |
| [[sdfl2012s100ktf]] | 1 | 2026-07-26 |
| [[sm02b-ghs-tb-lf-sn]] | 1 | 2026-07-26 |
| [[sm07b-ghs-tb-lf-sn]] | 1 | 2026-07-29 |
| [[sn74ahct1g125dbvr]] | 1 | 2026-07-26 |
| [[t37k3rgb-05c000112u1930]] | 1 | 2026-07-26 |
| [[tca9535pwr]] | 1 | 2026-07-31 |
| [[tlv7021dckr]] | 1 | 2026-07-29 |
| [[tlv7042dgkr]] | 1 | 2026-07-26 |
| [[tlv809k33dbvr]] | 1 | 2026-07-29 |
| [[tps2553dbvr-1]] | 1 | 2026-07-26 |
| [[tps61088rhlr]] | 1 | 2026-07-29 |
| [[usb4105-gf-a]] | 1 | 2026-07-26 |
<!-- V1-COMPONENT-CATALOG:END -->
## Concepts

Ideas, patterns, techniques. See `wiki/concept` pages.

| Page                                    | Confidence | source_count | Updated    |
| --------------------------------------- | ---------- | ------------ | ---------- |
| [[bitwiseid-method]]                    | high       | 1            | 2026-08-01 |
| [[bitwisexy-method]]                    | high       | 1            | 2026-07-24 |
| [[set-management-and-setid]]            | high       | 1            | 2026-07-24 |
| [[row-column-antenna-matrix-technique]] | high       | 4            | 2026-07-24 |
| [[pin-diode-antenna-switching]]         | high       | 1            | 2026-07-24 |
| [[jlcpcb-basic-part-sourcing]]          | medium     | 3            | 2026-07-25 |
| [[usb-c-pd-fast-charging]]              | high       | 6            | 2026-07-26 |
| [[usb-type-c-5v-current-advertisement]] | high       | 2            | 2026-07-29 |
| [[commercial-battery-subsystem]]        | high       | 4            | 2026-07-26 |
| [[fail-safe-cell-temperature-window]]   | high       | 4            | 2026-07-26 |
|                                         |            |              |            |

## Synthesis

Query answers filed back into the wiki. See `wiki/synthesis` pages.

| Page | Question | Updated |
| --- | --- | --- |
| [[tps2553-current-limit-error]] | Why did the original current-limit calculation fail? | 2026-07-25 |
| [[jlcpcb-matrix-bom-review]] | How can the matrix BOM be made unambiguous, stocked, and safe? | 2026-07-24 |
| [[verification-evidence-model]] | How are requirements, criteria, and tests kept synchronized? | 2026-07-25 |
| [[v1-component-proof]] | How is every fitted component tied to exact V1 evidence? | 2026-07-30 |
| [[v2-static-connectivity]] | How are schematic connectivity and the routed boards proven equivalent? | 2026-07-29 |
| [[v3-charge-interlock]] | How is the cell-temperature charge cutoff proven over every published tolerance? | 2026-07-29 |
| [[v3-led-rail-current-limit]] | Does the light-bar limiter pass the real load and clamp a fault? | 2026-07-29 |
| [[v3-buck-power-stage]] | What do the 3.3 V rail's passives do over their published tolerances? | 2026-07-29 |
| [[battery-format-and-module-alternatives]] | Which protected pack minimizes completed-unit cost and fits the rail? | 2026-07-30 |
| [[chessboard-quick-charge-architecture]] | How can recharge time become much shorter than useful play time? | 2026-07-26 |
| [[quick-charge-module-evaluation]] | Can a cheap purchased board de-risk quick charging? | 2026-07-26 |
| [[commercial-power-subsystem-selection]] | Which purchased subsystem should own the battery and charging? | 2026-07-26 |
| [[er-oledm3-12-1w-display-current]] | Is the display 320 mA or 2 mA? | 2026-08-01 |
| [[split-sensing-plane]] | Where may a board boundary cut a resonant sensing plane, and into how many pieces? | 2026-08-02 |
| [[pcba-cost-structure]] | What actually drives assembly cost at one-unit quantity, and where are the remaining savings? | 2026-08-02 |
