#include "core/move.h"

#include <stddef.h>

move_t move_make(square_t from, square_t to, piece_type_t promotion, uint8_t flags)
{
    move_t move;
    move.from = from;
    move.to = to;
    move.promotion = (uint8_t)promotion;
    move.flags = flags;
    return move;
}

piece_type_t move_promotion(const move_t *move)
{
    return (piece_type_t)move->promotion;
}

bool move_equal(const move_t *a, const move_t *b)
{
    /* Flags are part of identity. Two moves between the same squares with
     * different flags are different moves: a pawn reaching the fifth rank
     * beside an enemy pawn can be an ordinary push or an en-passant capture
     * depending on what stands there, and confusing them loses a piece. */
    return a->from == b->from && a->to == b->to &&
           a->promotion == b->promotion && a->flags == b->flags;
}

move_t move_null(void)
{
    return move_make(SQUARE_INVALID, SQUARE_INVALID, PIECE_TYPE_NONE, 0u);
}

bool move_is_null(const move_t *move)
{
    return move->from == SQUARE_INVALID && move->to == SQUARE_INVALID;
}

bool move_is_castle(const move_t *move)
{
    return (move->flags & (MOVE_FLAG_CASTLE_KING | MOVE_FLAG_CASTLE_QUEEN)) != 0u;
}

bool move_is_capture(const move_t *move)
{
    return (move->flags & MOVE_FLAG_CAPTURE) != 0u;
}

static char promotion_letter(piece_type_t type)
{
    switch (type) {
    case PIECE_TYPE_QUEEN:
        return 'q';
    case PIECE_TYPE_ROOK:
        return 'r';
    case PIECE_TYPE_BISHOP:
        return 'b';
    case PIECE_TYPE_KNIGHT:
        return 'n';
    default:
        return '\0';
    }
}

uint8_t move_to_text(const move_t *move, char *out, uint8_t capacity)
{
    if (out == NULL || capacity < 6) {
        return 0u;
    }
    if (!square_is_valid(move->from) || !square_is_valid(move->to)) {
        return 0u;
    }

    uint8_t length = 0u;
    out[length++] = square_file_letter(move->from);
    out[length++] = (char)('0' + square_rank(move->from));
    out[length++] = square_file_letter(move->to);
    out[length++] = (char)('0' + square_rank(move->to));

    const char promotion = promotion_letter(move_promotion(move));
    if (promotion != '\0') {
        out[length++] = promotion;
    }
    out[length] = '\0';
    return length;
}
