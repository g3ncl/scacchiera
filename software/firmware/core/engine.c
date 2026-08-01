#include "core/engine.h"

#include <string.h>

void engine_init(engine_state_t *state)
{
    memset(state, 0, sizeof(*state));
    board_snapshot_clear(&state->position);
    state->has_position = false;
}

engine_result_t engine_apply_snapshot(engine_state_t *state,
                                      const board_snapshot_t *snapshot)
{
    /* A fault must not become a position. The spec is explicit that faults
     * never change the stored position, so this guard belongs here rather
     * than in every caller. */
    if (snapshot->fault.fault != BOARD_FAULT_NONE) {
        return ENGINE_RESULT_NOT_IMPLEMENTED;
    }
    state->position = *snapshot;
    state->has_position = true;
    return ENGINE_RESULT_NOT_IMPLEMENTED;
}

bool engine_is_implemented(void)
{
    return false;
}
