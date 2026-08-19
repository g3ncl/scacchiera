#ifndef CHESSBOARD_CORE_PIECE_H
#define CHESSBOARD_CORE_PIECE_H

typedef enum {
    PIECE_TYPE_NONE = 0,
    PIECE_TYPE_PAWN,
    PIECE_TYPE_KNIGHT,
    PIECE_TYPE_BISHOP,
    PIECE_TYPE_ROOK,
    PIECE_TYPE_QUEEN,
    PIECE_TYPE_KING,
} piece_type_t;

typedef enum {
    PIECE_COLOR_WHITE = 0,
    PIECE_COLOR_BLACK,
} piece_color_t;

#endif
