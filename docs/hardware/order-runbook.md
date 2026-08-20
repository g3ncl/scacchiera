# Order runbook

One purchasing session, everything the build needs, in execution order. This is the step-by-step
companion to [ordering.md](ordering.md), which carries the rationale, the release conditions and
the per-board detail; when the two disagree, ordering.md wins. All paths are repo-relative;
artifacts regenerate with `make pcb-fab` and `make pcb-self-solder-order` on the bound-library
machine.

## 1. JLCPCB, boards and assembly

Upload only `<board>_gerbers.zip` for fabrication and the `_jlcpcb_upload_bom.csv` +
`_jlcpcb_upload_cpl.csv` pair for assembly. Never the `_max_assembly_` pair, never
`_bom_all_parts.csv`, never anything under `generated/panel/` or `generated/matrix/`.

| Board | Fabrication file | Assembly pair | Qty | Thickness | Finish |
| --- | --- | --- | --- | --- | --- |
| quad | `hardware/pcb/generated/quad/quad_gerbers.zip` | none, hand populated | 5 | **0.6 mm** | **OSP** |
| lightbar | `hardware/pcb/generated/lightbar/lightbar_gerbers.zip` | none, hand populated | 5 | 1.0 mm | HASL |
| hub | `hardware/pcb/generated/hub/hub_gerbers.zip` | `hub_jlcpcb_upload_bom.csv` + `hub_jlcpcb_upload_cpl.csv` | 5 | 1.0 mm | ENIG preferred, HASL acceptable |
| power | `hardware/pcb/generated/power/power_gerbers.zip` | `power_jlcpcb_upload_bom.csv` + `power_jlcpcb_upload_cpl.csv` | 5 | 1.0 mm | ENIG preferred, HASL acceptable |

Order form options on every board: 2 layers, 1 oz copper, 0.3 mm via drill (standard tier).

At order time, on the hub:

1. **U4 substitution.** The bound ESP32-C6-MINI-1U-N4 (C7558096) is not stocked; substitute
   ESP32-C6-MINI-1U-H4 (C20627095), same datasheet, wider temperature grade.
2. **J1 matcher.** If the matcher rejects C3020560 again, see the power-only USB-C fallback in
   [jlcpcb-sourcing.md](jlcpcb-sourcing.md). A hub without J1 has no power input.
3. **Placement preview.** Check every part before paying, especially J1, U3 and U4; rotate or
   nudge in their editor if a body sits wrong. See the DFM reconciliation in
   [ordering.md](ordering.md).
4. **Record the upload DFM result** in [planning.md](../planning.md), per the release conditions.

## 2. LCSC, hand-fitted parts

The cart is `hardware/pcb/generated/self_solder_order.csv`: every LCSC-source line at its Order
quantity. Import by the **LCSC Part #** column only; keyword matching invents wrong parts (a
search for C1046 once returned a Motorola DIP). Then add the accessory hardware LCSC stocks:

| Add to cart | Code | Qty |
| --- | --- | --- |
| Molex Micro-Fit housing 430250800, module-to-hub harness, both ends | C127351 | 2 |
| Molex Micro-Fit housing 430250200, cell link | C293523 | 1 |

Optional: LCSC's custom cable service (lcsc.com/customcables) can build all ten JST GH harnesses,
and it is the easiest way to get the four sensing cables at exactly equal length.

**Combine the LCSC and JLCPCB orders into one shipment**: place both, then ask
`support@lcsc.com` to combine them, or bind the JLCPCB order during LCSC checkout. It must happen
before either ships.

## 3. DigiKey

| Item | Order as | Qty |
| --- | --- | --- |
| Light-bar LEDs, Harvatek T37K3RGB-05C000112U1930 | `3147-T37K3RGB-05C000112U1930CT-ND` (cut tape) | 30 |
| Molex Micro-Fit female terminals 430300038, 18 AWG cell link and module harness | search the MPN | 30 |
| The 10 uH choke, only if LCSC's C882484 stock is gone | LQM21DH100M70L | 30 |

## 4. AliExpress and specialist shops

| Item | Where | Search | Qty |
| --- | --- | --- | --- |
| ER-OLEDM3.12-1W display modules | EastRising official store, or buydisplay.com direct | `EastRising 3.12 inch OLED 256x64 SSD1362` | 2 |
| AD Circus SLIX2 piece tags | Shop NFC (shopnfc.com) | catalog item, about 0.69 EUR each | 32 |
| Protected 21700 cell, wired leads | Keeppower official store | `Keeppower 21700 6000mAh protected` | 1 |
| JST GH 7-pin cables, double head | AliExpress | `GHR-07V-S cable assembly` | 7 (4 at exactly 100 mm) |
| JST GH 4-pin cables, double head | AliExpress | `GHR-04V-S cable assembly` | 3 |
| 2.4 GHz FPC antenna with pigtail | AliExpress | `2.4GHz FPC antenna MHF3 W.FL IPEX3` | 1 |
| 18 AWG silicone wire, red and black | anywhere | insulation outside diameter at most 1.85 mm | 1 m each |

Acceptance checks, each one a known failure mode:

- **Displays**: must be strapped four-wire SPI, BS[2:0] = 000 (assumption A2 in
  [assumptions.md](assumptions.md)). A wrong strap means a replacement, not rework.
- **Tags**: must be ICODE SLIX2, die-cut 21 mm or smaller. From any channel other than Shop NFC,
  verify the IC type with an NFC phone before fitting 32 of them.
- **GH cables**: the listing must say GH or GHR, not bare "JST 1.25", which on AliExpress usually
  means an unlocked PicoBlade clone that does not mate. The housing photo shows a friction-lock
  bump on top. The four sensing cables must all be the same length, 100 mm
  (`quad_geometry.HARNESS_LENGTH_MM`); equal beats short. Beep pin 1 to pin 1 before first power.
- **Antenna**: the connector is MHF3 / W.FL / IPEX3. U.FL (IPEX1) does not fit.
- **Cell**: packs often ship 22 AWG leads; the cell link wants 18 AWG within the 1.85 mm
  insulation limit, so expect to re-terminate. See [cell-assembly.md](cell-assembly.md) and
  [harnesses.md](harnesses.md).

## 5. After ordering

Record in [planning.md](../planning.md): each upload's DFM result, the J1 matcher outcome, the U4
substitution with its dated availability, and the accessory purchase links as V1 dated evidence.
Store the quad boards dry and populate them reasonably soon; OSP degrades with time and handling.
