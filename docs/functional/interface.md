# Interface

The local controls and feedback surfaces: two displays, two light bars, and one button. This is how
the board communicates and how a player drives it without a browser. It is independent of the
sensing architecture.

## Displays

Two OLED displays, one in each 50 mm player rail, each the 100 x 33 mm ER-OLEDM3.12-1W module. They
show clocks, setup messages, countdowns, faults, and battery state. During an unclocked game the
displays stay dark unless they need to communicate something.

The display glass is never preloaded: the display PCB is clamped against hard stops, and the button
sits outside the display cradle so it can be reached with a finger.

## Light bars

Two diffused rail bars, one per player, each a 120 x 8.5 mm custom PCB with 17 low-current LEDs behind
a replaceable diffuser. They show brief feedback: move accepted, error, result, WiFi state, and
countdowns. All components are on the front side, behind the diffuser.

## Button

A single button starts a new game (press), pauses or resumes the clock (short press during a game),
and gates maintenance actions such as provisioning (long hold with owner confirmation). It is placed
so it is reachable independently of the display cradle.

## Feedback semantics

- The displays carry text state: clocks, setup and start prompts, countdowns (resign, draw, low
  battery), faults, and battery level.
- The light bars carry brief, glanceable signals: move, error, result, WiFi, and countdown cues, and
  the red illegal-position flash on the offending side.
- When nothing needs communicating during an unclocked game, both surfaces stay dark to save power.

Brightness is configurable from the owner's browser client (see [gameplay.md](gameplay.md)).
