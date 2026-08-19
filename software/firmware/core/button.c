#include "core/button.h"

#include <string.h>

void button_init(button_t *state)
{
    memset(state, 0, sizeof(*state));
}

button_event_t button_update(button_t *state, bool pressed, uint32_t now_ms)
{
    if (pressed && !state->held) {
        state->held = true;
        state->long_reported = false;
        state->pressed_at_ms = now_ms;
        return BUTTON_EVENT_NONE;
    }
    if (pressed && state->held) {
        /* Unsigned delta, so the millisecond wrap is a non-event. */
        if (!state->long_reported &&
            (uint32_t)(now_ms - state->pressed_at_ms) >= BUTTON_LONG_HOLD_MS) {
            state->long_reported = true;
            return BUTTON_EVENT_LONG;
        }
        return BUTTON_EVENT_NONE;
    }
    if (!pressed && state->held) {
        state->held = false;
        /* A hold that already fired LONG is consumed; releasing it is not a
         * second gesture. */
        return state->long_reported ? BUTTON_EVENT_NONE : BUTTON_EVENT_SHORT;
    }
    return BUTTON_EVENT_NONE;
}
