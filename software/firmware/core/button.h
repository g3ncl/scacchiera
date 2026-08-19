#ifndef CHESSBOARD_CORE_BUTTON_H
#define CHESSBOARD_CORE_BUTTON_H

#include <stdbool.h>
#include <stdint.h>

/* Turning a sampled button level into the two gestures the functional spec
 * names: a short press (start a game, pause or resume the clock) and a long
 * hold (the provisioning gate). Time arrives as a parameter, like everywhere
 * else in core/, so a test never waits. */

/* Below this a release is a short press; at or past it the hold is long. Three
 * seconds, matching the deliberate-gesture timing the spec uses elsewhere. */
#define BUTTON_LONG_HOLD_MS 3000u

typedef enum {
    BUTTON_EVENT_NONE = 0,
    BUTTON_EVENT_SHORT,
    BUTTON_EVENT_LONG,
} button_event_t;

typedef struct {
    bool held;
    bool long_reported;
    uint32_t pressed_at_ms;
} button_t;

void button_init(button_t *state);

/* Feeds one sample. SHORT fires on release, LONG fires once while still held
 * (so the player gets feedback without having to let go blind). */
button_event_t button_update(button_t *state, bool pressed, uint32_t now_ms);

#endif
