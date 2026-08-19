#ifndef CHESSBOARD_CORE_RESULT_H
#define CHESSBOARD_CORE_RESULT_H

#include <stdbool.h>

#include "core/movegen.h"
#include "core/position.h"
#include "core/repetition.h"

/* How a game ends.
 *
 * docs/functional/gameplay.md splits endings in two, and the split is the
 * whole point of this file: checkmate, stalemate, dead positions, fivefold
 * repetition and the 75-move rule finish the game by themselves, while
 * threefold repetition and the 50-move rule are only ever shown as hints for a
 * player to claim. Automatic and claimable are different things and merging
 * them would end games nobody asked to end. */

typedef enum {
    GAME_RESULT_NONE = 0,
    GAME_RESULT_WHITE_WINS,
    GAME_RESULT_BLACK_WINS,
    GAME_RESULT_DRAW,
} game_result_t;

typedef enum {
    RESULT_REASON_NONE = 0,
    RESULT_REASON_CHECKMATE,
    RESULT_REASON_STALEMATE,
    RESULT_REASON_DEAD_POSITION,
    RESULT_REASON_FIVEFOLD,
    RESULT_REASON_SEVENTY_FIVE_MOVE,
    RESULT_REASON_FLAG_FALL,
    RESULT_REASON_FLAG_FALL_INSUFFICIENT,
    RESULT_REASON_RESIGNATION,
    RESULT_REASON_AGREED_DRAW,
} result_reason_t;

typedef struct {
    game_result_t result;
    result_reason_t reason;
    /* Displayed, never acted on. */
    bool hint_threefold;
    bool hint_fifty_move;
} result_report_t;

/* Evaluated after every committed move. Reports only the automatic endings. */
void result_evaluate(const position_t *position, const repetition_t *ledger,
                     move_list_t *scratch, result_report_t *report);

/* GAME-RESULT-001. Flag fall ends the game, except that a player who cannot
 * possibly mate does not win on time. */
game_result_t result_flag_fall(const position_t *position, piece_color_t flagged,
                               result_reason_t *reason);

/* The decidable subset and nothing beyond it: king against king, king and
 * bishop against king, king and knight against king, and king and bishop
 * against king and bishop with both bishops on squares of the same colour.
 *
 * Blocked pawn walls and the other positions that are dead in principle are
 * deliberately NOT detected. Deciding those in general is not something a rule
 * this size can do, and claiming otherwise would end games wrongly. This limit
 * is recorded rather than hidden. */
bool result_dead_position(const position_t *position);

/* A weaker question than the one above, and used only for flag fall: could
 * `side` deliver mate by any series of legal moves, however cooperative the
 * opponent. False when it has no pawn, rook or queen and at most one minor
 * piece, so king and two knights wins on time even though it cannot force
 * mate, which is what FIDE says.
 *
 * Kept separate from result_dead_position on purpose. Merging them gets king
 * and two knights wrong on time and opposite-coloured bishops wrong as a dead
 * position, in opposite directions. */
bool result_can_mate(const position_t *position, piece_color_t side);

#endif
