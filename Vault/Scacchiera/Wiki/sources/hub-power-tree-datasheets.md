---
type: source-summary
tags:
  - wiki/source
date_updated: 2026-07-25
source_file: "Datasheets/MCP73871T-2CCI-ML_C511310.pdf, Datasheets/TPS63802DLAR_C2845237.pdf, Datasheets/TPS61023DRLR_C919459.pdf, Datasheets/TPS2553DBVR-1_C111738.pdf, Datasheets/TCA9535PWR_C130204.pdf, Datasheets/SN74AHCT1G125DBVR_C7484.pdf, Datasheets/USBLC6-2SC6_C2687116.pdf"
source_title: "Hub power tree and logic: seven manufacturer datasheets"
publisher: Microchip, Texas Instruments, UMW
---

# Hub power tree and logic datasheets

The seven parts that set the [hub board](../../../../docs/hardware/hub.md)'s rail values, filed
together because the design's resistor choices are only checkable against them. Ingested to close
the V1 gap in [simulation-workflow](../../../../docs/simulation-workflow.md).

## The equations the design depends on

| Part | What it sets | Equation and reference |
| --- | --- | --- |
| MCP73871 | fast charge current | `IREG = 1000 / RPROG1` (kohm, mA), section 5.1.2 eq 5-1, RPROG1 valid 1 to 20 kohm |
| MCP73871 | charge termination | `ITERM = 1000 / RPROG3` (kohm, mA), section 4.7 eq 4-2, RPROG3 valid 5 to 100 kohm |
| TPS63802 | 3V3 output | `R1 = R2 * (VOUT/VFB - 1)`, **VFB = 500 mV**, section 10.2.2.5 eq 3, R2 max 100 kohm |
| TPS61023 | 5 V output | `R1 = (VOUT/VREF - 1) * R2`, **VREF = 595 mV typ**, section 8.2.2.1 eq 4, R2 under 300 kohm |
| TPS2553 | current limit | `IOSmin = 25230/R^1.016`, `IOSnom = 23950/R^0.977`, `IOSmax = 22980/R^0.94` (kohm, mA), section 9.5.1, valid 15 to 232 kohm |

[vfb_tps63802_mv::500] [vref_tps61023_mv::595] [ilim_valid_kohm::15-232]

## Checked against the design

| Designator | Value | Datasheet result | Verdict |
| --- | --- | --- | --- |
| R7 (PROG1) | 2.0 k | 500 mA fast charge | in range, sensible for one cell |
| R6 (PROG3) | 24.9 k | 40.2 mA termination, C/12 | in range |
| R13/R14 | 511 k / 91 k | 0.5 x (1 + 511/91) = **3.31 V** | correct for 3V3, R2 under 100 k |
| R15/R16 | 732 k / 100 k | 0.595 x (1 + 732/100) = **4.95 V** | correct for 5 V, and TI's own worked example uses exactly 732 k / 100 k with a 1 uH inductor |
| **R17 (ILIM)** | **was 82 k** | **287 / 323 / 365 mA** | **failed: below the 448 mA the light bars draw. Changed to 39 k, giving 609 / 667 / 734 mA** |

The R17 error is the one this ingest caught. The 82 k value had been justified by a recalled
formula rather than the datasheet, and it would have latched the light bars off on any bright cue.
See [[tps2553-current-limit-error]].

## Other values worth having on record

- **MCP73871 THERM** (section 3.15, 4.9): an internal 50 uA source biases a **10 kohm NTC**, compared
  against 1.24 V and 0.25 V thresholds. Outside that window charging suspends. The hub brings this out
  on J10, so **the 10 k NTC is a purchased accessory on no BOM**.
- **MCP73871 VLBO**: not an equation. The low-battery threshold is factory trimmed and selected by
  ordering code; the `-2CCI` part decodes to **3.1 V with 150 mV hysteresis**. This is what the
  functional spec's save-and-shutdown behavior hangs off.
- **TPS61023 output capability**: not tabulated. Derived from the datasheet's own equation 1 with
  ILIM 3.7 A, L 1 uH, 1 MHz, eta 0.9: about **1.6 A at 3.0 V in**, 2.4 A at 4.2 V in. The datasheet's
  worked example claims 1.5 A across 2.7 to 4.35 V. Marked Derived, not Datasheet.
- **TPS63802**: 2 A rated for VIN at or above 2.3 V at VOUT 3.3 V.
- **SN74AHCT1G125** (section 5.3): **VIH 2 V min, VIL 0.8 V max at a 5 V supply**, fixed TTL levels.
  This is precisely why the part is in the design: a 3.3 V GPIO clears 2 V, so the buffer accepts
  MCU logic and drives the LED chain at 5 V, above the fitted Harvatek LED's 3.1 V minimum VIH.
- **TCA9535**: INT is open-drain active-low on any port edge.

## Caveat on the ESD part

`USBLC6-2SC6_C2687116.pdf` is a **UMW (UTD Semiconductor)** document, not STMicroelectronics.
st.com refused every request from this environment, and LCSC lists UMW as the manufacturer for
C2687116: it is a pin and spec compatible clone sold under ST's part number. Every USBLC6 value on
record here comes from that UMW sheet. If genuine ST silicon matters for this line, confirm with the
supplier.

Related: [[esp32-c6-mini-1u]], [[sk6805mini-e]], [[jlcpcb]]
