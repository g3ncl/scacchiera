#ifndef CHESSBOARD_CORE_POSITION_H
#define CHESSBOARD_CORE_POSITION_H

#include <stdbool.h>
#include <stdint.h>

#include "core/move.h"
#include "core/piece.h"
#include "core/snapshot.h"
#include "core/square.h"

/* A complete chess position, and the rules for changing it.
 *
 * This is the state. A board_snapshot_t is an observation: it says what the
 * sensors read, and it cannot say whose turn it is, whether castling is still
 * available, or which pawn may be taken en passant. Those are facts about the
 * game, not about the copper, so the game owns them and every observation is
 * matched against this rather than replacing it.
 *
 * The board is a plain 8x8 mailbox indexed exactly as square_t, a1 = 0 through
 * h8 = 63. A 0x88 board would make the off-board test one instruction cheaper
 * and would introduce a second square numbering alongside square_t,
 * board_snapshot_t, scan_join, the display and PGN. This project already keeps
 * test_matrix_encoding.c specifically to stop a transposed index reaching the
 * board, and generation runs about three times a second, so the cheaper test
 * would be bought with exactly the class of bug that matters most here. */

/* One byte per square: bits 0 to 2 the type, bit 3 the colour. A byte rather
 * than the two enums because piece_type_t is an int, which would make a
 * position 512 bytes and a stored game 40 KB. */
typedef uint8_t position_piece_t;
#define POSITION_PIECE_NONE ((position_piece_t)0u)

position_piece_t position_piece_make(piece_color_t color, piece_type_t type);
piece_type_t position_piece_type(position_piece_t piece);
piece_color_t position_piece_color(position_piece_t piece);
bool position_piece_is(position_piece_t piece, piece_color_t color, piece_type_t type);

#define POSITION_CASTLE_WHITE_KING 0x01u
#define POSITION_CASTLE_WHITE_QUEEN 0x02u
#define POSITION_CASTLE_BLACK_KING 0x04u
#define POSITION_CASTLE_BLACK_QUEEN 0x08u

/* The 75-move rule ends a game at 150 plies, so the counter never needs to
 * exceed that and saturating below 255 keeps it a byte. */
#define POSITION_HALFMOVE_MAX 255u

typedef struct {
    position_piece_t board[BOARD_SQUARES];
    piece_color_t side_to_move;
    uint8_t castling;
    /* The square a capturing pawn would move TO, not the square the captured
     * pawn stands on. SQUARE_INVALID when there is no such capture. */
    square_t en_passant;
    uint8_t halfmove_clock;
    uint16_t fullmove_number;
} position_t;

void position_clear(position_t *position);
void position_init_standard(position_t *position);

position_piece_t position_at(const position_t *position, square_t square);
square_t position_king_square(const position_t *position, piece_color_t color);

/* Applies a move that is already known to be legal. movegen and movederive are
 * the only producers of moves and both produce legal ones, so re-validating
 * here would be a second rule implementation to keep in step with the first. */
void position_make_move(position_t *position, const move_t *move);

/* Compares the logical position with a typed physical reading and reports the
 * squares that disagree, lowest first. Fills at most `capacity` of them but
 * always returns the true count, so a caller can tell "two differ" from "more
 * than I asked for".
 *
 * UID is deliberately ignored. Two pieces of the same colour and type are
 * interchangeable in chess, so a player who swaps identical rooks has changed
 * nothing and must not read as having moved. An unreadable square always
 * counts as differing: not knowing is not the same as agreeing. */
uint8_t position_snapshot_diff(const position_t *position,
                               const board_snapshot_t *snapshot,
                               square_t *differing, uint8_t capacity);

/* True when the physical board shows exactly this position. On false,
 * `first_mismatch` names the lowest differing square, which is what
 * GAME-START-003 requires a rejected start position to report. */
bool position_matches_snapshot(const position_t *position,
                               const board_snapshot_t *snapshot,
                               square_t *first_mismatch);

/* Identity for repetition: the board, the side to move, the castling rights
 * and the en-passant square. Deliberately excludes the halfmove clock and the
 * move number, because FIDE repetition does not consider them.
 *
 * FNV-1a over the canonical bytes rather than Zobrist. Zobrist exists to be
 * updated incrementally inside a search, and there is no search here; a 781
 * entry table and an incremental update path would buy nothing and would add a
 * class of silent, unreproducible bug. */
uint64_t position_key(const position_t *position);

/* FEN, which exists mainly so movegen can be tested against published perft
 * positions. Returns false on anything malformed rather than half-parsing. */
bool position_from_fen(position_t *position, const char *fen);
uint8_t position_to_fen(const position_t *position, char *out, uint8_t capacity);

#endif
