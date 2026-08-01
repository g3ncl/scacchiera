#ifndef CHESSBOARD_CORE_ENGINE_H
#define CHESSBOARD_CORE_ENGINE_H

#include "core/snapshot.h"

/* Deliberately a stub. docs/software/architecture.md orders the work by what a
 * board can teach us: no rule in docs/functional/gameplay.md can invalidate a
 * PCB, so the rules engine waits behind the drivers that can. The layers above
 * and below it are exercised through this interface in the meantime, and V5's
 * generated-sequence bullet stays open until it is real. */

typedef enum {
    ENGINE_RESULT_NOT_IMPLEMENTED = 0,
    ENGINE_RESULT_ACCEPTED,
    ENGINE_RESULT_REJECTED,
} engine_result_t;

typedef struct {
    board_snapshot_t position;
    bool has_position;
} engine_state_t;

void engine_init(engine_state_t *state);

/* Records the snapshot as the current position and reports that rule
 * evaluation is not implemented. It never reports ACCEPTED or REJECTED, so a
 * caller that mistakes the stub for a working engine fails loudly rather than
 * silently treating an unvalidated move as legal. */
engine_result_t engine_apply_snapshot(engine_state_t *state,
                                      const board_snapshot_t *snapshot);

bool engine_is_implemented(void);

#endif
