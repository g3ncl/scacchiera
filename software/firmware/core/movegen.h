#ifndef CHESSBOARD_CORE_MOVEGEN_H
#define CHESSBOARD_CORE_MOVEGEN_H

#include <stdbool.h>
#include <stdint.h>

#include "core/move.h"
#include "core/position.h"

/* Legal move generation.
 *
 * Legality is decided by making the move and asking whether the mover's king
 * is attacked, not by tracking pins. That is the simplest correct approach and
 * it gets the two rules a pin-aware generator most often gets wrong for free:
 * the en-passant capture that opens a discovered check along the fifth rank,
 * and a pinned piece capturing the very piece that pins it. Pin-aware
 * generation exists to make a search fast, and there is no search here: this
 * runs about three times a second. */

/* 218 is the largest number of legal moves a legal position is known to hold.
 * 220 leaves headroom without claiming a bound nobody has proved. */
#define MOVEGEN_MAX_MOVES 220

typedef struct {
    move_t moves[MOVEGEN_MAX_MOVES];
    uint8_t count;
} move_list_t;

void movegen_legal(const position_t *position, move_list_t *list);

/* Cheaper than generating when the answer is only "is there one", which is the
 * question checkmate and stalemate actually ask.
 *
 * The scratch list is the caller's because a move_list_t is 884 bytes and an
 * ESP-IDF task stack defaults to 3584. Every list in this design is owned by a
 * long-lived struct so the deepest call chain puts none of them on the stack. */
bool movegen_has_legal_move(const position_t *position, move_list_t *scratch);

bool movegen_square_attacked(const position_t *position, square_t square,
                             piece_color_t by);
bool movegen_in_check(const position_t *position, piece_color_t side);

#endif
