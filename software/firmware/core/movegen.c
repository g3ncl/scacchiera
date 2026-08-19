#include "core/movegen.h"

/* The board is padded to 10 by 12 for generation only, so a slide that leaves
 * the board lands on a sentinel instead of wrapping onto the far file. Two
 * ranks of padding top and bottom because a knight can jump two ranks.
 *
 * These tables are pure arithmetic and test_movegen.c regenerates them from
 * square_from_file_rank rather than trusting the literals, for the same reason
 * test_matrix_encoding.c pins the selection map: a transposed index is not a
 * compile error, it is a board that plays the wrong game. */
#define PADDED_SQUARES 120
#define OFF_BOARD (-1)

/* Padded index of a board square. One rank is ten, so up is +10. */
static const int8_t PADDED_OF_SQUARE[BOARD_SQUARES] = {
    21, 22, 23, 24, 25, 26, 27, 28,
    31, 32, 33, 34, 35, 36, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48,
    51, 52, 53, 54, 55, 56, 57, 58,
    61, 62, 63, 64, 65, 66, 67, 68,
    71, 72, 73, 74, 75, 76, 77, 78,
    81, 82, 83, 84, 85, 86, 87, 88,
    91, 92, 93, 94, 95, 96, 97, 98,
};

static const int8_t SQUARE_OF_PADDED[PADDED_SQUARES] = {
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1,  0,  1,  2,  3,  4,  5,  6,  7, -1,
    -1,  8,  9, 10, 11, 12, 13, 14, 15, -1,
    -1, 16, 17, 18, 19, 20, 21, 22, 23, -1,
    -1, 24, 25, 26, 27, 28, 29, 30, 31, -1,
    -1, 32, 33, 34, 35, 36, 37, 38, 39, -1,
    -1, 40, 41, 42, 43, 44, 45, 46, 47, -1,
    -1, 48, 49, 50, 51, 52, 53, 54, 55, -1,
    -1, 56, 57, 58, 59, 60, 61, 62, 63, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
};

static const int8_t KNIGHT_OFFSETS[8] = {-21, -19, -12, -8, 8, 12, 19, 21};
static const int8_t KING_OFFSETS[8] = {-11, -10, -9, -1, 1, 9, 10, 11};
static const int8_t BISHOP_OFFSETS[4] = {-11, -9, 9, 11};
static const int8_t ROOK_OFFSETS[4] = {-10, -1, 1, 10};

/* Resolves a padded index to a board square, or SQUARE_INVALID off the board. */
static square_t board_square(int padded)
{
    if (padded < 0 || padded >= PADDED_SQUARES) {
        return SQUARE_INVALID;
    }
    const int8_t square = SQUARE_OF_PADDED[padded];
    return (square == OFF_BOARD) ? SQUARE_INVALID : (square_t)square;
}

static int padded_index(square_t square)
{
    return (int)PADDED_OF_SQUARE[square];
}

static piece_color_t opponent_of(piece_color_t color)
{
    return (color == PIECE_COLOR_WHITE) ? PIECE_COLOR_BLACK : PIECE_COLOR_WHITE;
}

static bool attacked_by_offsets(const position_t *position, int from, piece_color_t by,
                                piece_type_t type, const int8_t *offsets, uint8_t count)
{
    const position_piece_t wanted = position_piece_make(by, type);
    for (uint8_t index = 0u; index < count; index++) {
        const square_t target = board_square(from + offsets[index]);
        if (target != SQUARE_INVALID && position->board[target] == wanted) {
            return true;
        }
    }
    return false;
}

static bool attacked_by_slider(const position_t *position, int from, piece_color_t by,
                               piece_type_t type, const int8_t *offsets, uint8_t count)
{
    const position_piece_t wanted = position_piece_make(by, type);
    const position_piece_t queen = position_piece_make(by, PIECE_TYPE_QUEEN);

    for (uint8_t index = 0u; index < count; index++) {
        int cursor = from;
        for (;;) {
            cursor += offsets[index];
            const square_t target = board_square(cursor);
            if (target == SQUARE_INVALID) {
                break;
            }
            const position_piece_t piece = position->board[target];
            if (piece == POSITION_PIECE_NONE) {
                continue;
            }
            if (piece == wanted || piece == queen) {
                return true;
            }
            break;
        }
    }
    return false;
}

bool movegen_square_attacked(const position_t *position, square_t square,
                             piece_color_t by)
{
    if (!square_is_valid(square)) {
        return false;
    }
    const int from = padded_index(square);

    /* Pawns are asked about first because they are the commonest attacker and
     * the cheapest test. A white pawn attacking this square stands one rank
     * below it, so the search runs against the direction of travel. */
    static const int8_t WHITE_PAWN_ATTACKERS[2] = {-9, -11};
    static const int8_t BLACK_PAWN_ATTACKERS[2] = {9, 11};
    const int8_t *pawn_offsets =
        (by == PIECE_COLOR_WHITE) ? WHITE_PAWN_ATTACKERS : BLACK_PAWN_ATTACKERS;
    if (attacked_by_offsets(position, from, by, PIECE_TYPE_PAWN, pawn_offsets, 2u)) {
        return true;
    }
    if (attacked_by_offsets(position, from, by, PIECE_TYPE_KNIGHT, KNIGHT_OFFSETS, 8u)) {
        return true;
    }
    if (attacked_by_offsets(position, from, by, PIECE_TYPE_KING, KING_OFFSETS, 8u)) {
        return true;
    }
    if (attacked_by_slider(position, from, by, PIECE_TYPE_BISHOP, BISHOP_OFFSETS, 4u)) {
        return true;
    }
    if (attacked_by_slider(position, from, by, PIECE_TYPE_ROOK, ROOK_OFFSETS, 4u)) {
        return true;
    }
    return false;
}

bool movegen_in_check(const position_t *position, piece_color_t side)
{
    const square_t king = position_king_square(position, side);
    if (king == SQUARE_INVALID) {
        return false;
    }
    return movegen_square_attacked(position, king, opponent_of(side));
}

static void add_move(move_list_t *list, move_t move)
{
    if (list->count < MOVEGEN_MAX_MOVES) {
        list->moves[list->count++] = move;
    }
}

static void add_pawn_move(move_list_t *list, square_t from, square_t to, uint8_t flags,
                          piece_color_t mover)
{
    const uint8_t last_rank = (mover == PIECE_COLOR_WHITE) ? 8u : 1u;
    if (square_rank(to) != last_rank) {
        add_move(list, move_make(from, to, PIECE_TYPE_NONE, flags));
        return;
    }
    /* Every promotion choice is a distinct move, which is what lets move
     * derivation identify which piece the player physically placed. */
    static const piece_type_t choices[4] = {PIECE_TYPE_QUEEN, PIECE_TYPE_ROOK,
                                            PIECE_TYPE_BISHOP, PIECE_TYPE_KNIGHT};
    for (uint8_t index = 0u; index < 4u; index++) {
        add_move(list, move_make(from, to, choices[index], flags));
    }
}

static void generate_pawn(const position_t *position, move_list_t *list, square_t from,
                          piece_color_t mover)
{
    const int forward = (mover == PIECE_COLOR_WHITE) ? 10 : -10;
    const uint8_t start_rank = (mover == PIECE_COLOR_WHITE) ? 2u : 7u;
    const int from_padded = padded_index(from);

    const square_t ahead = board_square(from_padded + forward);
    if (ahead != SQUARE_INVALID && position->board[ahead] == POSITION_PIECE_NONE) {
        add_pawn_move(list, from, ahead, 0u, mover);

        if (square_rank(from) == start_rank) {
            const square_t two_ahead = board_square(from_padded + (2 * forward));
            if (two_ahead != SQUARE_INVALID &&
                position->board[two_ahead] == POSITION_PIECE_NONE) {
                add_move(list, move_make(from, two_ahead, PIECE_TYPE_NONE,
                                         MOVE_FLAG_DOUBLE_PAWN));
            }
        }
    }

    const int captures[2] = {forward - 1, forward + 1};
    for (uint8_t index = 0u; index < 2u; index++) {
        const square_t target = board_square(from_padded + captures[index]);
        if (target == SQUARE_INVALID) {
            continue;
        }
        const position_piece_t piece = position->board[target];
        if (piece != POSITION_PIECE_NONE && position_piece_color(piece) != mover) {
            add_pawn_move(list, from, target, MOVE_FLAG_CAPTURE, mover);
        } else if (piece == POSITION_PIECE_NONE && target == position->en_passant) {
            add_move(list, move_make(from, target, PIECE_TYPE_NONE,
                                     MOVE_FLAG_CAPTURE | MOVE_FLAG_EN_PASSANT));
        }
    }
}

static void generate_stepper(const position_t *position, move_list_t *list, square_t from,
                             piece_color_t mover, const int8_t *offsets, uint8_t count)
{
    const int from_padded = padded_index(from);
    for (uint8_t index = 0u; index < count; index++) {
        const square_t target = board_square(from_padded + offsets[index]);
        if (target == SQUARE_INVALID) {
            continue;
        }
        const position_piece_t piece = position->board[target];
        if (piece == POSITION_PIECE_NONE) {
            add_move(list, move_make(from, target, PIECE_TYPE_NONE, 0u));
        } else if (position_piece_color(piece) != mover) {
            add_move(list, move_make(from, target, PIECE_TYPE_NONE, MOVE_FLAG_CAPTURE));
        }
    }
}

static void generate_slider(const position_t *position, move_list_t *list, square_t from,
                            piece_color_t mover, const int8_t *offsets, uint8_t count)
{
    const int from_padded = padded_index(from);
    for (uint8_t index = 0u; index < count; index++) {
        int cursor = from_padded;
        for (;;) {
            cursor += offsets[index];
            const square_t target = board_square(cursor);
            if (target == SQUARE_INVALID) {
                break;
            }
            const position_piece_t piece = position->board[target];
            if (piece == POSITION_PIECE_NONE) {
                add_move(list, move_make(from, target, PIECE_TYPE_NONE, 0u));
                continue;
            }
            if (position_piece_color(piece) != mover) {
                add_move(list, move_make(from, target, PIECE_TYPE_NONE, MOVE_FLAG_CAPTURE));
            }
            break;
        }
    }
}

/* Castling is the one move whose legality is not fully covered by the
 * make-and-test filter: the king may not pass through an attacked square, and
 * a resulting position says nothing about the square it crossed. */
static void generate_castling(const position_t *position, move_list_t *list,
                              piece_color_t mover)
{
    const square_t king_square = position_king_square(position, mover);
    if (king_square == SQUARE_INVALID) {
        return;
    }
    const piece_color_t enemy = opponent_of(mover);
    if (movegen_square_attacked(position, king_square, enemy)) {
        return;
    }

    const square_t home = (mover == PIECE_COLOR_WHITE) ? (square_t)4u : (square_t)60u;
    if (king_square != home) {
        return;
    }
    const uint8_t kingside_right = (mover == PIECE_COLOR_WHITE) ? POSITION_CASTLE_WHITE_KING
                                                                : POSITION_CASTLE_BLACK_KING;
    const uint8_t queenside_right = (mover == PIECE_COLOR_WHITE)
                                        ? POSITION_CASTLE_WHITE_QUEEN
                                        : POSITION_CASTLE_BLACK_QUEEN;
    const position_piece_t rook = position_piece_make(mover, PIECE_TYPE_ROOK);

    const square_t kingside_rook = (square_t)(home + 3);
    const square_t kingside_transit = (square_t)(home + 1);
    const square_t kingside_target = (square_t)(home + 2);
    const square_t queenside_rook = (square_t)(home - 4);
    const square_t queenside_transit = (square_t)(home - 1);
    const square_t queenside_target = (square_t)(home - 2);
    const square_t queenside_knight = (square_t)(home - 3);

    if ((position->castling & kingside_right) != 0u &&
        position->board[kingside_rook] == rook &&
        position->board[kingside_transit] == POSITION_PIECE_NONE &&
        position->board[kingside_target] == POSITION_PIECE_NONE &&
        !movegen_square_attacked(position, kingside_transit, enemy)) {
        add_move(list, move_make(home, kingside_target, PIECE_TYPE_NONE,
                                 MOVE_FLAG_CASTLE_KING));
    }

    if ((position->castling & queenside_right) != 0u &&
        position->board[queenside_rook] == rook &&
        position->board[queenside_transit] == POSITION_PIECE_NONE &&
        position->board[queenside_target] == POSITION_PIECE_NONE &&
        /* b1 and b8 must be empty for the rook to pass, but the king never
         * crosses them, so they are not tested for attack. */
        position->board[queenside_knight] == POSITION_PIECE_NONE &&
        !movegen_square_attacked(position, queenside_transit, enemy)) {
        add_move(list, move_make(home, queenside_target, PIECE_TYPE_NONE,
                                 MOVE_FLAG_CASTLE_QUEEN));
    }
}

static void generate_pseudo_legal(const position_t *position, move_list_t *list)
{
    const piece_color_t mover = position->side_to_move;
    list->count = 0u;

    for (square_t from = 0u; from < BOARD_SQUARES; from++) {
        const position_piece_t piece = position->board[from];
        if (piece == POSITION_PIECE_NONE || position_piece_color(piece) != mover) {
            continue;
        }
        switch (position_piece_type(piece)) {
        case PIECE_TYPE_PAWN:
            generate_pawn(position, list, from, mover);
            break;
        case PIECE_TYPE_KNIGHT:
            generate_stepper(position, list, from, mover, KNIGHT_OFFSETS, 8u);
            break;
        case PIECE_TYPE_KING:
            generate_stepper(position, list, from, mover, KING_OFFSETS, 8u);
            break;
        case PIECE_TYPE_BISHOP:
            generate_slider(position, list, from, mover, BISHOP_OFFSETS, 4u);
            break;
        case PIECE_TYPE_ROOK:
            generate_slider(position, list, from, mover, ROOK_OFFSETS, 4u);
            break;
        case PIECE_TYPE_QUEEN:
            generate_slider(position, list, from, mover, BISHOP_OFFSETS, 4u);
            generate_slider(position, list, from, mover, ROOK_OFFSETS, 4u);
            break;
        case PIECE_TYPE_NONE:
        default:
            break;
        }
    }
    generate_castling(position, list, mover);
}

static bool leaves_king_safe(const position_t *position, const move_t *move)
{
    position_t after = *position;
    position_make_move(&after, move);
    return !movegen_in_check(&after, position->side_to_move);
}

void movegen_legal(const position_t *position, move_list_t *list)
{
    generate_pseudo_legal(position, list);

    uint8_t kept = 0u;
    for (uint8_t index = 0u; index < list->count; index++) {
        if (leaves_king_safe(position, &list->moves[index])) {
            list->moves[kept++] = list->moves[index];
        }
    }
    list->count = kept;
}

bool movegen_has_legal_move(const position_t *position, move_list_t *scratch)
{
    /* Still generates the pseudo-legal list, but stops filtering at the first
     * survivor. Checkmate and stalemate ask this question, not for the list. */
    generate_pseudo_legal(position, scratch);
    for (uint8_t index = 0u; index < scratch->count; index++) {
        if (leaves_king_safe(position, &scratch->moves[index])) {
            return true;
        }
    }
    return false;
}
