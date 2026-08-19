#include "core/stability.h"

#include <string.h>

void stability_init(stability_t *state)
{
    memset(state, 0, sizeof(*state));
    board_snapshot_clear(&state->previous);
    board_snapshot_clear(&state->candidate);
}

static bool square_changed(const board_snapshot_t *a, const board_snapshot_t *b, square_t square)
{
    const square_reading_t *left = &a->squares[square];
    const square_reading_t *right = &b->squares[square];
    if (left->state != right->state) {
        return true;
    }
    /* Only an occupied square carries an identity worth comparing; on an empty
     * one the remaining fields are stale bytes. */
    return left->state == SQUARE_STATE_OCCUPIED && left->uid != right->uid;
}

bool stability_unstable_square(const stability_t *state, square_t *square)
{
    for (square_t index = 0; index < BOARD_SQUARES; index++) {
        if (state->changes[index] >= STABILITY_UNSTABLE_CHANGES) {
            if (square != NULL) {
                *square = index;
            }
            return true;
        }
    }
    return false;
}

bool stability_update(stability_t *state, const board_snapshot_t *raw,
                      uint32_t now_ms, board_snapshot_t *stable)
{
    /* A faulted sweep is not evidence of anything. It cannot confirm the
     * current candidate and it must not replace it, so agreement is reset and
     * the sweep is otherwise ignored. Faults never become a position. */
    if (raw->fault.fault != BOARD_FAULT_NONE) {
        state->agreements = 0;
        return false;
    }

    /* The change window is a sliding budget, restarted rather than decayed per
     * square: a board that has been quiet for two seconds has earned a clean
     * slate everywhere. */
    if (!state->has_previous || (uint32_t)(now_ms - state->window_start_ms) >= STABILITY_WINDOW_MS) {
        memset(state->changes, 0, sizeof(state->changes));
        state->window_start_ms = now_ms;
    }

    if (state->has_previous) {
        for (square_t square = 0; square < BOARD_SQUARES; square++) {
            if (square_changed(&state->previous, raw, square) &&
                state->changes[square] < UINT8_MAX) {
                state->changes[square]++;
            }
        }
    }
    state->previous = *raw;
    state->has_previous = true;

    if (state->has_candidate && board_snapshot_equal(&state->candidate, raw)) {
        if (state->agreements < UINT8_MAX) {
            state->agreements++;
        }
    } else {
        state->candidate = *raw;
        state->has_candidate = true;
        state->agreements = 1;
        /* A different position is a new claim, so a previous emission no
         * longer suppresses this one. */
        state->emitted = false;
    }

    if (state->agreements < STABILITY_REQUIRED_AGREEMENTS || state->emitted) {
        return false;
    }
    state->emitted = true;
    *stable = state->candidate;
    return true;
}
