# Assumption register

Values the design uses that are not backed by a filed manufacturer datasheet. Each one is a
deliberate decision to proceed rather than wait on a supplier, taken so development is not blocked
by correspondence.

This file exists so those decisions stay visible and cheap to pay down. Every row states what is
assumed, why it is credible, what actually happens if it is wrong, and where it gets measured.
Nothing here is hidden in a margin field.

**Read this before an order.** [simulation-workflow.md](../simulation-workflow.md) treats an
assumed or waived critical value as a V1 failure, so every row below is a waiver against the V8
test-article gate and the V9 review. That has no bearing on design, layout, simulation or firmware
work, which continues normally. It bears only on releasing a fabrication order, and the honest
position at that point is that these were accepted knowingly.

## Register

| ID | Assumption | Basis | If wrong | Measured at |
| --- | --- | --- | --- | --- |
| **A1** | Molex 430300038 contact is rated **8.5 A**. | Consistent across independent distributor listings. Molex PS-43045 revision M1 stops at 20 AWG at 5 A and has no 18 AWG row; Molex's servers did not serve a current revision. | Nothing. At the alternative 5.0 A the cell link still has 11 percent margin on 4.442 A RMS. This is the safest row here. | V8 contact temperature rise at full load |
| **A2** | The two ER-OLEDM3.12-1W modules ship strapped for **four-wire SPI**. | BuyDisplay sells and documents the part as a four-wire SPI breakout for Arduino and Raspberry Pi. The datasheet never states how the mode is selected; the back view shows 0-ohm jumper pairs R3/R9, R5/R8 and R10/R11/R12. | The display does not respond at all. Fix is reworking those jumpers before assembly, not a board change. Fails loudly and early, which is why it is an acceptable assumption. | First firmware bring-up |
| **A3** | Display pins 7 (R/W) and 8 (E/RD) need **external grounding**. | Datasheet section 4.1 says both must be connected to VSS in serial mode, without qualifying that the module does it. Conservative reading. | Nothing. If the module already grounds them the solder bridge is redundant and harmless. | First bring-up |
| **A4** | The preliminary revision 1.0 display datasheet's numbers hold. | Its 320 mA maximum is independently corroborated to 312 to 331 mA by a comparable 3.12 inch 256 by 64 panel from another manufacturer. | The load budget moves. 320 mA per display is already the conservative direction. | V8 display current |
| **A5** | The Keeppower 1S1P 21700 pack's protection meets [cell-assembly.md](cell-assembly.md). | The distributor lists a Seiko protection PCB and 12 A continuous discharge. Seiko's 1S family sits within the required windows at typical thresholds. The exact IC is unpublished. | Over-discharge tripping above 2.8 V shortens runtime; overcharge tripping at 4.2 V nuisance-trips every charge; overcurrent below 6.502 A turns a stress condition into a dead board. This is the highest-consequence row. | V8 protection characterisation |
| **A6** | The pack's shipped leads are re-terminated, and re-led to 18 AWG if thinner. | Packs of this class commonly ship 20 to 22 AWG with a small connector. The design needs 18 AWG into a keyed Micro-Fit with insulation at most 1.85 mm. | Hand work at assembly, already expected. | Incoming inspection |
| **A7** | The charge window is **0 to 40 degrees Celsius**. | Borrowed from `PISUGAR3_PLUS_safety.md`, a module no longer bound. Conservative for any consumer lithium-ion cell. | Probably conservative. A cell datasheet may permit wider, which would only relax the interlock. | Replaced when a cell datasheet is filed |
| **A8** | The AD Circus SLIX2 tag coil resonates against the SL2S2602's 23.5 pF input capacitance. | Avery Dennison publishes no coil inductance, turn count or resonant frequency for any converted inlay. The tag coil is back-solved from the resonance condition. | The V4 coupling model is bounded rather than exact. Read range per cell shifts. | V8 assembled RF |
| **A9** | Loaded tag Q is bounded from the SL2S2602's 40 uW minimum input power. | NXP publishes no equivalent parallel resistance at minimum operating power. | Same as A8. | V8 assembled RF |
| **A10** | The Harvatek T37K3RGB datasheet's numbers hold. | It is marked **Preliminary**, dated 2025-05-19, the third preliminary document in the build after the display module and its controller. Its bit timings and RGB order are specific enough to be deliberate rather than placeholder. | Wrong bit timings show as flicker or no output at bring-up; a wrong colour order shows as a green illegal-move flash. Both fail visibly and immediately. | First light-bar bring-up |
| **A11** | A mated JST GH contact pair adds **2 to 8 nH**, used only by the split sensing plane. | JST publishes no contact inductance for the GH series, and no connector vendor at this price does. 2 nH is about a 2 mm straight contact; 8 nH allows the housing's full mated length plus the pad transitions at both boards. | Nothing, and that is demonstrated rather than argued. `hardware/sim/quad_rf.py` sweeps the whole fourfold range and the bus band moves by less than one sweep step, so no criterion in the split depends on the value. This is the cheapest row here. | V8 bus sweep, if the split ships |

## What this costs at the gate

Eleven rows, of which A1, A3, A4, A6, A7, A10 and A11 are low consequence or conservative in the
safe direction, or fail visibly at first bring-up. A11 is the only one that has been shown not to
matter rather than argued to be small: its whole range is swept and nothing moves.

The three that actually matter:

- **A5**, the cell protection thresholds, because getting them wrong is a safety and behaviour
  problem rather than a margin problem.
- **A2**, the display interface mode, because it decides whether the displays work at all. It
  fails immediately and visibly at bring-up, which is the best kind of wrong.
- **A8 and A9** together, because they are what stops V4 from being a fully datasheet-sourced
  electromagnetic model.

A V8 test article measures all of them. None needs to be resolved before then, and none blocks
schematic, layout, simulation or firmware work in the meantime.
