#ifndef CHESSBOARD_CORE_MOVEDERIVE_H
#define CHESSBOARD_CORE_MOVEDERIVE_H

#include <stdbool.h>
#include <stdint.h>

#include "core/movegen.h"
#include "core/position.h"
#include "core/snapshot.h"

/* Deciding which legal move, if any, turned a known position into the position
 * the sensors now report.
 *
 * The obvious design switches on how many squares changed: one for a quiet
 * move, two for a capture, three for en passant, four for castling. It is a
 * trap. It reimplements the rules a second time, in a second place, with
 * different bugs, and it cannot tell a half-finished castle from an illegal
 * board.
 *
 * This inverts it. Generate the legal moves, apply each one to a scratch
 * position, and compare the result with what the board actually shows. Capture,
 * castling, en passant and the choice of promotion piece all fall out of that
 * single comparison with no special case, and the move that comes back is
 * legal by construction rather than by a second check afterwards.
 *
 * The rule that makes the product usable rather than merely correct: a board
 * that differs only by pieces having been lifted is never an error. Lifting the
 * captured piece, then your own, then placing yours, is how a human captures,
 * and the board passes through that state every single time. */

typedef enum {
    MOVEDERIVE_UNCHANGED = 0,
    MOVEDERIVE_MOVE,
    /* A pawn stands on its promotion square and has not yet been replaced.
     * Not a completed move, not a fault, and not illegal. */
    MOVEDERIVE_PROMOTION_PENDING,
    /* Pieces are in transit. Wait, do not judge. */
    MOVEDERIVE_INCOMPLETE,
    /* A square could not be read at all, so nothing can be concluded about it.
     * Separate from ILLEGAL because not knowing and knowing something wrong
     * are different things, and only one of them is the player's fault. */
    MOVEDERIVE_UNREADABLE,
    MOVEDERIVE_ILLEGAL,
    /* Two legal moves would produce the same physical board. Unreachable in
     * standard chess; present because guessing is forbidden, so a variant or a
     * bug has to fail loudly rather than have one picked for it. */
    MOVEDERIVE_AMBIGUOUS,
} movederive_result_t;

/* Enough to report on; the result does not depend on the count, because any
 * number of lifted pieces is equally INCOMPLETE. */
#define MOVEDERIVE_MAX_LIFTED 8

typedef struct {
    movederive_result_t result;
    /* Valid for MOVE. For PROMOTION_PENDING only from and to are meaningful. */
    move_t move;
    square_t lifted[MOVEDERIVE_MAX_LIFTED];
    uint8_t lifted_count;
    /* The square to point the player at, for ILLEGAL, UNREADABLE and
     * AMBIGUOUS. GAME-ILLEGAL-001 and GAME-START-003 both require naming a
     * square rather than reporting a general failure. */
    square_t offender;
} movederive_report_t;

/* Owned by the caller so the deepest call chain puts no move_list_t on a task
 * stack; see movegen.h. */
typedef struct {
    move_list_t legal;
    position_t scratch;
} movederive_context_t;

void movederive(movederive_context_t *context, const position_t *before,
                const board_snapshot_t *snapshot, movederive_report_t *report);

/* True when one of the lifted squares held a piece of `color` before. This is
 * what commits a provisional move: the opponent touching one of their own
 * pieces is their acceptance of the move that was just played. */
bool movederive_lifted_by(const movederive_report_t *report, const position_t *before,
                          piece_color_t color, square_t *square);

#endif
