#include "core/position.h"

#include <string.h>

#define PIECE_TYPE_MASK 0x07u
#define PIECE_COLOR_BIT 0x08u

/* Home squares of the four castling rooks, which are also the squares whose
 * occupation decides whether a right survives. */
#define SQUARE_A1 0u
#define SQUARE_E1 4u
#define SQUARE_H1 7u
#define SQUARE_A8 56u
#define SQUARE_E8 60u
#define SQUARE_H8 63u

position_piece_t position_piece_make(piece_color_t color, piece_type_t type)
{
    if (type == PIECE_TYPE_NONE) {
        /* A colourless empty square. Encoding "black nothing" as 8 would make
         * an empty square test as occupied. */
        return POSITION_PIECE_NONE;
    }
    position_piece_t piece = (position_piece_t)((uint8_t)type & PIECE_TYPE_MASK);
    if (color == PIECE_COLOR_BLACK) {
        piece = (position_piece_t)(piece | PIECE_COLOR_BIT);
    }
    return piece;
}

piece_type_t position_piece_type(position_piece_t piece)
{
    return (piece_type_t)(piece & PIECE_TYPE_MASK);
}

piece_color_t position_piece_color(position_piece_t piece)
{
    return ((piece & PIECE_COLOR_BIT) != 0u) ? PIECE_COLOR_BLACK : PIECE_COLOR_WHITE;
}

bool position_piece_is(position_piece_t piece, piece_color_t color, piece_type_t type)
{
    return piece != POSITION_PIECE_NONE && position_piece_type(piece) == type &&
           position_piece_color(piece) == color;
}

void position_clear(position_t *position)
{
    memset(position, 0, sizeof(*position));
    position->side_to_move = PIECE_COLOR_WHITE;
    position->en_passant = SQUARE_INVALID;
    position->fullmove_number = 1u;
}

void position_init_standard(position_t *position)
{
    static const piece_type_t back_rank[BOARD_FILES] = {
        PIECE_TYPE_ROOK, PIECE_TYPE_KNIGHT, PIECE_TYPE_BISHOP, PIECE_TYPE_QUEEN,
        PIECE_TYPE_KING, PIECE_TYPE_BISHOP, PIECE_TYPE_KNIGHT, PIECE_TYPE_ROOK,
    };

    position_clear(position);
    for (uint8_t file = 0u; file < BOARD_FILES; file++) {
        position->board[file] = position_piece_make(PIECE_COLOR_WHITE, back_rank[file]);
        position->board[BOARD_FILES + file] =
            position_piece_make(PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
        position->board[48u + file] =
            position_piece_make(PIECE_COLOR_BLACK, PIECE_TYPE_PAWN);
        position->board[56u + file] = position_piece_make(PIECE_COLOR_BLACK, back_rank[file]);
    }
    position->castling = POSITION_CASTLE_WHITE_KING | POSITION_CASTLE_WHITE_QUEEN |
                         POSITION_CASTLE_BLACK_KING | POSITION_CASTLE_BLACK_QUEEN;
}

position_piece_t position_at(const position_t *position, square_t square)
{
    if (!square_is_valid(square)) {
        return POSITION_PIECE_NONE;
    }
    return position->board[square];
}

square_t position_king_square(const position_t *position, piece_color_t color)
{
    const position_piece_t king = position_piece_make(color, PIECE_TYPE_KING);
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        if (position->board[square] == king) {
            return square;
        }
    }
    /* No king is not a position this product can reach through legal play, but
     * movegen must not index off the board while a caller is building one. */
    return SQUARE_INVALID;
}

/* Rights are cleared whenever a king or a rook leaves its home square, and
 * whenever anything lands on a rook's home square, which covers the rook being
 * captured where it stands. */
static uint8_t rights_lost_by_square(square_t square)
{
    switch (square) {
    case SQUARE_E1:
        return POSITION_CASTLE_WHITE_KING | POSITION_CASTLE_WHITE_QUEEN;
    case SQUARE_H1:
        return POSITION_CASTLE_WHITE_KING;
    case SQUARE_A1:
        return POSITION_CASTLE_WHITE_QUEEN;
    case SQUARE_E8:
        return POSITION_CASTLE_BLACK_KING | POSITION_CASTLE_BLACK_QUEEN;
    case SQUARE_H8:
        return POSITION_CASTLE_BLACK_KING;
    case SQUARE_A8:
        return POSITION_CASTLE_BLACK_QUEEN;
    default:
        return 0u;
    }
}

/* The square the captured pawn actually stands on, which is beside the mover
 * rather than under it. */
static square_t en_passant_victim(square_t to, piece_color_t mover)
{
    return (mover == PIECE_COLOR_WHITE) ? (square_t)(to - BOARD_FILES)
                                        : (square_t)(to + BOARD_FILES);
}

/* Whether an enemy pawn is placed to actually make the capture.
 *
 * Setting the en-passant square unconditionally after a double push would make
 * two positions that are identical to both players hash differently, so
 * fivefold repetition would silently never fire. The residual gap is an
 * adjacent enemy pawn that is pinned, where the capture is not really
 * available; closing that would make position depend on movegen, and it is
 * recorded as a limit instead. */
static bool en_passant_is_available(const position_t *position, square_t arrival,
                                    piece_color_t mover)
{
    const piece_color_t enemy =
        (mover == PIECE_COLOR_WHITE) ? PIECE_COLOR_BLACK : PIECE_COLOR_WHITE;
    const position_piece_t enemy_pawn = position_piece_make(enemy, PIECE_TYPE_PAWN);
    const uint8_t file = (uint8_t)(arrival % BOARD_FILES);
    const uint8_t last_file = (uint8_t)(BOARD_FILES - 1);

    if (file > 0u && position->board[arrival - 1u] == enemy_pawn) {
        return true;
    }
    if (file < last_file && position->board[arrival + 1u] == enemy_pawn) {
        return true;
    }
    return false;
}

void position_make_move(position_t *position, const move_t *move)
{
    const position_piece_t piece = position->board[move->from];
    const piece_type_t type = position_piece_type(piece);
    const piece_color_t mover = position->side_to_move;
    const bool resets_clock =
        (type == PIECE_TYPE_PAWN) || ((move->flags & MOVE_FLAG_CAPTURE) != 0u);

    position->board[move->from] = POSITION_PIECE_NONE;

    if ((move->flags & MOVE_FLAG_EN_PASSANT) != 0u) {
        position->board[en_passant_victim(move->to, mover)] = POSITION_PIECE_NONE;
    }

    if (move_is_castle(move)) {
        /* The rook's travel is fixed by which side the king went to, so it is
         * derived rather than listed: a table of four would have to agree with
         * the four moves movegen produces. */
        const square_t rank_base = (square_t)(move->from - (move->from % BOARD_FILES));
        const bool kingside = (move->flags & MOVE_FLAG_CASTLE_KING) != 0u;
        const square_t rook_from =
            kingside ? (square_t)(rank_base + 7u) : rank_base;
        const square_t rook_to =
            kingside ? (square_t)(move->to - 1u) : (square_t)(move->to + 1u);
        position->board[rook_to] = position->board[rook_from];
        position->board[rook_from] = POSITION_PIECE_NONE;
    }

    const piece_type_t promotion = move_promotion(move);
    position->board[move->to] = (promotion == PIECE_TYPE_NONE)
                                    ? piece
                                    : position_piece_make(mover, promotion);

    position->castling &=
        (uint8_t)~(rights_lost_by_square(move->from) | rights_lost_by_square(move->to));

    if ((move->flags & MOVE_FLAG_DOUBLE_PAWN) != 0u) {
        const square_t skipped = (square_t)((move->from + move->to) / 2u);
        position->en_passant =
            en_passant_is_available(position, move->to, mover) ? skipped : SQUARE_INVALID;
    } else {
        position->en_passant = SQUARE_INVALID;
    }

    if (resets_clock) {
        position->halfmove_clock = 0u;
    } else if (position->halfmove_clock < POSITION_HALFMOVE_MAX) {
        position->halfmove_clock++;
    }

    if (mover == PIECE_COLOR_BLACK) {
        position->fullmove_number++;
    }
    position->side_to_move =
        (mover == PIECE_COLOR_WHITE) ? PIECE_COLOR_BLACK : PIECE_COLOR_WHITE;
}

static bool square_agrees(const position_t *position, const board_snapshot_t *snapshot,
                          square_t square)
{
    const square_reading_t *reading = &snapshot->squares[square];
    const position_piece_t expected = position->board[square];

    switch (reading->state) {
    case SQUARE_STATE_EMPTY:
        return expected == POSITION_PIECE_NONE;
    case SQUARE_STATE_OCCUPIED:
        return position_piece_is(expected, reading->color, reading->type);
    case SQUARE_STATE_UNREADABLE:
    default:
        /* Not knowing is not agreeing. A square the sensing could not resolve
         * must never be reported as matching, or a fault becomes a position. */
        return false;
    }
}

uint8_t position_snapshot_diff(const position_t *position,
                               const board_snapshot_t *snapshot,
                               square_t *differing, uint8_t capacity)
{
    uint8_t count = 0u;
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        if (square_agrees(position, snapshot, square)) {
            continue;
        }
        if (differing != NULL && count < capacity) {
            differing[count] = square;
        }
        count++;
    }
    return count;
}

bool position_matches_snapshot(const position_t *position,
                               const board_snapshot_t *snapshot,
                               square_t *first_mismatch)
{
    square_t lowest = SQUARE_INVALID;
    const uint8_t count = position_snapshot_diff(position, snapshot, &lowest, 1u);
    if (count == 0u) {
        return true;
    }
    if (first_mismatch != NULL) {
        *first_mismatch = lowest;
    }
    return false;
}

#define FNV_OFFSET_BASIS 0xcbf29ce484222325ull
#define FNV_PRIME 0x00000100000001b3ull

uint64_t position_key(const position_t *position)
{
    uint64_t hash = FNV_OFFSET_BASIS;

    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        hash ^= (uint64_t)position->board[square];
        hash *= FNV_PRIME;
    }
    hash ^= (uint64_t)position->side_to_move;
    hash *= FNV_PRIME;
    hash ^= (uint64_t)position->castling;
    hash *= FNV_PRIME;
    hash ^= (uint64_t)position->en_passant;
    hash *= FNV_PRIME;
    return hash;
}

static piece_type_t type_from_letter(char letter)
{
    switch (letter) {
    case 'p':
        return PIECE_TYPE_PAWN;
    case 'n':
        return PIECE_TYPE_KNIGHT;
    case 'b':
        return PIECE_TYPE_BISHOP;
    case 'r':
        return PIECE_TYPE_ROOK;
    case 'q':
        return PIECE_TYPE_QUEEN;
    case 'k':
        return PIECE_TYPE_KING;
    default:
        return PIECE_TYPE_NONE;
    }
}

static char letter_from_piece(position_piece_t piece)
{
    /* Indexed by the three type bits, so all eight values need a slot even
     * though only six name a piece. */
    static const char letters[8] = {'\0', 'p', 'n', 'b', 'r', 'q', 'k', '\0'};
    const piece_type_t type = position_piece_type(piece);
    char letter = letters[(uint8_t)type];
    if (position_piece_color(piece) == PIECE_COLOR_WHITE && letter != '\0') {
        letter = (char)(letter - ('a' - 'A'));
    }
    return letter;
}

bool position_from_fen(position_t *position, const char *fen)
{
    if (fen == NULL) {
        return false;
    }
    position_clear(position);

    uint8_t rank = 7u;
    uint8_t file = 0u;
    const char *cursor = fen;

    for (; *cursor != '\0' && *cursor != ' '; cursor++) {
        const char symbol = *cursor;
        if (symbol == '/') {
            if (file != BOARD_FILES || rank == 0u) {
                return false;
            }
            rank--;
            file = 0u;
            continue;
        }
        if (symbol >= '1' && symbol <= '8') {
            file = (uint8_t)(file + (uint8_t)(symbol - '0'));
            if (file > BOARD_FILES) {
                return false;
            }
            continue;
        }

        const bool is_black = (symbol >= 'a' && symbol <= 'z');
        const char lower = is_black ? symbol : (char)(symbol + ('a' - 'A'));
        const piece_type_t type = type_from_letter(lower);
        if (type == PIECE_TYPE_NONE || file >= BOARD_FILES) {
            return false;
        }
        position->board[(rank * BOARD_FILES) + file] = position_piece_make(
            is_black ? PIECE_COLOR_BLACK : PIECE_COLOR_WHITE, type);
        file++;
    }
    if (rank != 0u || file != BOARD_FILES) {
        return false;
    }

    if (*cursor != ' ') {
        return false;
    }
    cursor++;
    if (*cursor == 'w') {
        position->side_to_move = PIECE_COLOR_WHITE;
    } else if (*cursor == 'b') {
        position->side_to_move = PIECE_COLOR_BLACK;
    } else {
        return false;
    }
    cursor++;

    if (*cursor != ' ') {
        return false;
    }
    cursor++;
    if (*cursor == '-') {
        cursor++;
    } else {
        for (; *cursor != '\0' && *cursor != ' '; cursor++) {
            switch (*cursor) {
            case 'K':
                position->castling |= POSITION_CASTLE_WHITE_KING;
                break;
            case 'Q':
                position->castling |= POSITION_CASTLE_WHITE_QUEEN;
                break;
            case 'k':
                position->castling |= POSITION_CASTLE_BLACK_KING;
                break;
            case 'q':
                position->castling |= POSITION_CASTLE_BLACK_QUEEN;
                break;
            default:
                return false;
            }
        }
    }

    if (*cursor != ' ') {
        return false;
    }
    cursor++;
    if (*cursor == '-') {
        cursor++;
    } else {
        const char file_letter = *cursor++;
        const char rank_digit = *cursor++;
        if (rank_digit < '1' || rank_digit > '8') {
            return false;
        }
        const square_t target =
            square_from_file_rank(file_letter, (uint8_t)(rank_digit - '0'));
        if (!square_is_valid(target)) {
            return false;
        }
        position->en_passant = target;
    }

    /* The two counters are optional: most published perft positions carry them
     * and some test fixtures do not, and neither affects move generation. */
    if (*cursor == ' ') {
        cursor++;
        uint32_t halfmove = 0u;
        while (*cursor >= '0' && *cursor <= '9') {
            halfmove = (halfmove * 10u) + (uint32_t)(*cursor - '0');
            cursor++;
        }
        position->halfmove_clock =
            (halfmove > POSITION_HALFMOVE_MAX) ? (uint8_t)POSITION_HALFMOVE_MAX
                                               : (uint8_t)halfmove;
    }
    if (*cursor == ' ') {
        cursor++;
        uint32_t fullmove = 0u;
        while (*cursor >= '0' && *cursor <= '9') {
            fullmove = (fullmove * 10u) + (uint32_t)(*cursor - '0');
            cursor++;
        }
        if (fullmove > 0u) {
            position->fullmove_number = (uint16_t)fullmove;
        }
    }
    return true;
}

/* Appends one character if it fits, and counts it either way so the caller can
 * discover the length it needed. */
static void append(char *out, uint8_t capacity, uint8_t *length, char value)
{
    if (out != NULL && ((unsigned)(*length) + 1u) < (unsigned)capacity) {
        out[*length] = value;
    }
    (*length)++;
}

uint8_t position_to_fen(const position_t *position, char *out, uint8_t capacity)
{
    uint8_t length = 0u;

    for (uint8_t rank = 8u; rank > 0u; rank--) {
        uint8_t empty = 0u;
        for (uint8_t file = 0u; file < BOARD_FILES; file++) {
            const position_piece_t piece =
                position->board[((rank - 1u) * BOARD_FILES) + file];
            if (piece == POSITION_PIECE_NONE) {
                empty++;
                continue;
            }
            if (empty > 0u) {
                append(out, capacity, &length, (char)('0' + empty));
                empty = 0u;
            }
            append(out, capacity, &length, letter_from_piece(piece));
        }
        if (empty > 0u) {
            append(out, capacity, &length, (char)('0' + empty));
        }
        if (rank > 1u) {
            append(out, capacity, &length, '/');
        }
    }

    append(out, capacity, &length, ' ');
    append(out, capacity, &length,
           (position->side_to_move == PIECE_COLOR_WHITE) ? 'w' : 'b');
    append(out, capacity, &length, ' ');

    if (position->castling == 0u) {
        append(out, capacity, &length, '-');
    } else {
        if ((position->castling & POSITION_CASTLE_WHITE_KING) != 0u) {
            append(out, capacity, &length, 'K');
        }
        if ((position->castling & POSITION_CASTLE_WHITE_QUEEN) != 0u) {
            append(out, capacity, &length, 'Q');
        }
        if ((position->castling & POSITION_CASTLE_BLACK_KING) != 0u) {
            append(out, capacity, &length, 'k');
        }
        if ((position->castling & POSITION_CASTLE_BLACK_QUEEN) != 0u) {
            append(out, capacity, &length, 'q');
        }
    }

    append(out, capacity, &length, ' ');
    if (square_is_valid(position->en_passant)) {
        append(out, capacity, &length, square_file_letter(position->en_passant));
        append(out, capacity, &length, (char)('0' + square_rank(position->en_passant)));
    } else {
        append(out, capacity, &length, '-');
    }

    if (out != NULL && capacity > 0u) {
        out[(length < capacity) ? length : (uint8_t)(capacity - 1u)] = '\0';
    }
    return length;
}
