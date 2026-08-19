#ifndef CHESSBOARD_CORE_REPETITION_H
#define CHESSBOARD_CORE_REPETITION_H

#include <stdint.h>

/* How often the current position has occurred.
 *
 * The window is bounded by the 75-move rule rather than by the length of the
 * game: 150 plies without a pawn move or a capture ends the game anyway, and a
 * repetition cannot span an irreversible move because no earlier position can
 * recur once a pawn has advanced or a piece has left the board. So the ledger
 * is cleared on those moves rather than grown, and it never needs to hold a
 * whole game. */

#define REPETITION_MAX_PLIES 152

typedef struct {
    uint64_t keys[REPETITION_MAX_PLIES];
    uint8_t count;
} repetition_t;

/* Starts a new window at `key`: at the start of a game, and again after a
 * capture, a pawn move or a lost castling right, because nothing before those
 * can ever come back. */
void repetition_reset(repetition_t *ledger, uint64_t key);

void repetition_push(repetition_t *ledger, uint64_t key);

/* How many times this key appears, including the current position. Threefold
 * is 3, fivefold is 5. */
uint8_t repetition_count(const repetition_t *ledger, uint64_t key);

#endif
