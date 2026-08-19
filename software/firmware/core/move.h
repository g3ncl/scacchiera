#ifndef CHESSBOARD_CORE_MOVE_H
#define CHESSBOARD_CORE_MOVE_H

#include <stdbool.h>
#include <stdint.h>

#include "core/piece.h"
#include "core/square.h"

/* One chess move, in four bytes.
 *
 * Four rather than two packed into a uint16_t because the history is 600 plies
 * at most, so 2.4 KB against 1.2 KB buys nothing worth the bit twiddling, and
 * a struct with named fields is what a reviewer can check against the rules.
 *
 * The flags describe what the move does, not what it is worth. They exist so a
 * caller can render SAN and update castling rights without re-deriving the
 * geometry that movegen already knew. */

#define MOVE_FLAG_CAPTURE 0x01u
#define MOVE_FLAG_DOUBLE_PAWN 0x02u
/* Implies CAPTURE. The captured pawn is not on the destination square, which
 * is the whole reason this needs its own flag. */
#define MOVE_FLAG_EN_PASSANT 0x04u
#define MOVE_FLAG_CASTLE_KING 0x08u
#define MOVE_FLAG_CASTLE_QUEEN 0x10u

typedef struct {
    square_t from;
    square_t to;
    /* piece_type_t stored narrow: the enum is an int, and four of those would
     * make a move sixteen bytes. PIECE_TYPE_NONE unless the move promotes. */
    uint8_t promotion;
    uint8_t flags;
} move_t;

move_t move_make(square_t from, square_t to, piece_type_t promotion, uint8_t flags);
piece_type_t move_promotion(const move_t *move);
bool move_equal(const move_t *a, const move_t *b);

/* A move no legal generator can produce, used where "no move" has to be a
 * value rather than a flag. Distinguishable from a1a1, which is also not a
 * legal move but is a different thing to say. */
move_t move_null(void);
bool move_is_null(const move_t *move);

bool move_is_castle(const move_t *move);
bool move_is_capture(const move_t *move);

/* Long algebraic: "e2e4", or "e7e8q" when it promotes. Lower case, because
 * this feeds logs and the browser client rather than a display; the 5x7 font
 * has no lower case and present.c upper-cases what it draws. Returns the
 * length written, or 0 when the buffer is too small. */
uint8_t move_to_text(const move_t *move, char *out, uint8_t capacity);

#endif
