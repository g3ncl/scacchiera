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

## USB-C charging

With the board idle and connected through a compliant 9 V, 3 A USB-C Power Delivery source and
cable, charging from 10 percent to 80 percent takes no more than 90 minutes and charging from 10
percent to the normal full-charge termination takes no more than 150 minutes at 20 to 25 degrees
Celsius.

The board remains usable while connected to USB. Power-path management gives the running system
priority and reduces battery charge current when the negotiated input power is insufficient. A
lower-power USB source charges safely at a reduced rate and is never loaded beyond its advertised
capability.

## Battery safety

The fitted battery assembly has independent overcharge, over-discharge, overcurrent, and short
circuit protection. Charging is permitted only while the cell temperature is within the qualified
charge range measured by a thermistor attached to the cell. The board reports temperature-limited
or source-limited charging instead of presenting it as a fault-free fast-charge cycle.
