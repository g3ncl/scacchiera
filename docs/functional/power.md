# Battery and charging

The user-visible energy requirements for a cordless board. These requirements define useful play
time and recharge behavior without fixing a cell format, charger IC, or USB implementation.

## Cordless runtime

The board provides at least ten hours of representative clocked gameplay from a full battery at
20 to 25 degrees Celsius. The representative profile keeps both displays active, maintains the
browser connection, scans the complete board often enough to meet the gameplay response time, and
uses the light bars for normal event feedback rather than continuous decorative animation.

Maximum-brightness continuous white lighting is a stress condition, not the representative runtime
profile. The owner interface reports the estimated remaining play time as well as battery level.

## Peak output

The battery subsystem supplies a regulated 5 V at 2 A. This 10 W rating is a stress capability for
coincident display, radio, reader, and lighting activity, not the representative runtime profile.
The output remains within regulation across the qualified cell-voltage range without depending on
USB input power.

## USB-C charging

With the board idle and connected through a compliant 5 V, 2 A USB source and cable, charging from
10 percent to 80 percent takes no more than 240 minutes and charging from 10 percent to the normal
full-charge termination takes no more than 360 minutes at 20 to 25 degrees Celsius. USB Power
Delivery negotiation is not required. USB-C Power Delivery chargers, including laptop chargers,
are supported through their mandatory 5 V output. The board neither requests nor accepts 9 V,
12 V, 15 V, 20 V, or PPS output.

Recharging is an overnight or between-sessions activity, not a fast top-up. The product trades
charge speed for the cost of the power subsystem, so a one-amp charger is sufficient and the
board is not required to reach a usable charge inside one game.

The board remains usable while connected to USB. Power-path management gives the running system
priority and reduces battery charge current when the available input power is insufficient. A
lower-power USB source charges safely at a reduced rate and is never loaded beyond its advertised
capability.

## Battery safety

The fitted battery assembly has independent overcharge, over-discharge, overcurrent, and short
circuit protection. Charging is permitted only while the cell temperature is within the qualified
charge range measured by a thermistor attached to the cell. The board reports temperature-limited
or source-limited charging instead of presenting it as a fault-free fast-charge cycle.

A single cylindrical cell may lie lengthwise along the player rail. Its length consumes rail length;
its diameter, holder, insulation, and wiring must fit the rail cross-section. The complete protected
assembly and every series contact are rated for the worst-case current at the minimum permitted cell
voltage, not merely for the average current at nominal voltage.
