#include "unity.h"

#include <string.h>

#include "core/position.h"

static position_t position;

void setUp(void)
{
    position_init_standard(&position);
}

void tearDown(void) {}

static square_t sq(char file, uint8_t rank)
{
    return square_from_file_rank(file, rank);
}

static void expect_piece(char file, uint8_t rank, piece_color_t color, piece_type_t type)
{
    TEST_ASSERT_TRUE(position_piece_is(position_at(&position, sq(file, rank)), color, type));
}

static void test_the_piece_byte_round_trips_for_every_piece(void)
{
    static const piece_type_t types[6] = {PIECE_TYPE_PAWN,  PIECE_TYPE_KNIGHT,
                                          PIECE_TYPE_BISHOP, PIECE_TYPE_ROOK,
                                          PIECE_TYPE_QUEEN, PIECE_TYPE_KING};
    for (uint8_t index = 0u; index < 6u; index++) {
        for (uint8_t color = 0u; color < 2u; color++) {
            const position_piece_t piece =
                position_piece_make((piece_color_t)color, types[index]);
            TEST_ASSERT_EQUAL_INT(types[index], position_piece_type(piece));
            TEST_ASSERT_EQUAL_INT(color, position_piece_color(piece));
            TEST_ASSERT_NOT_EQUAL_UINT8(POSITION_PIECE_NONE, piece);
        }
    }
}

/* A black empty square must not encode as a non-zero byte, or every empty
 * square on black's half of the board reads as occupied. */
static void test_an_empty_square_has_no_colour(void)
{
    TEST_ASSERT_EQUAL_UINT8(POSITION_PIECE_NONE,
                            position_piece_make(PIECE_COLOR_BLACK, PIECE_TYPE_NONE));
    TEST_ASSERT_EQUAL_UINT8(POSITION_PIECE_NONE,
                            position_piece_make(PIECE_COLOR_WHITE, PIECE_TYPE_NONE));
}

static void test_the_standard_start_is_where_it_should_be(void)
{
    expect_piece('a', 1, PIECE_COLOR_WHITE, PIECE_TYPE_ROOK);
    expect_piece('e', 1, PIECE_COLOR_WHITE, PIECE_TYPE_KING);
    expect_piece('d', 1, PIECE_COLOR_WHITE, PIECE_TYPE_QUEEN);
    expect_piece('e', 2, PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    expect_piece('e', 8, PIECE_COLOR_BLACK, PIECE_TYPE_KING);
    expect_piece('d', 8, PIECE_COLOR_BLACK, PIECE_TYPE_QUEEN);
    expect_piece('h', 7, PIECE_COLOR_BLACK, PIECE_TYPE_PAWN);
    TEST_ASSERT_EQUAL_UINT8(POSITION_PIECE_NONE, position_at(&position, sq('e', 4)));
    TEST_ASSERT_EQUAL_INT(PIECE_COLOR_WHITE, position.side_to_move);
    TEST_ASSERT_EQUAL_UINT8(0x0Fu, position.castling);
    TEST_ASSERT_EQUAL_UINT8(SQUARE_INVALID, position.en_passant);
    TEST_ASSERT_EQUAL_UINT16(1u, position.fullmove_number);
}

static void test_king_squares_are_found(void)
{
    TEST_ASSERT_EQUAL_UINT8(sq('e', 1), position_king_square(&position, PIECE_COLOR_WHITE));
    TEST_ASSERT_EQUAL_UINT8(sq('e', 8), position_king_square(&position, PIECE_COLOR_BLACK));
}

static void test_a_quiet_move_advances_the_clock_and_the_turn(void)
{
    const move_t knight = move_make(sq('g', 1), sq('f', 3), PIECE_TYPE_NONE, 0u);
    position_make_move(&position, &knight);

    expect_piece('f', 3, PIECE_COLOR_WHITE, PIECE_TYPE_KNIGHT);
    TEST_ASSERT_EQUAL_UINT8(POSITION_PIECE_NONE, position_at(&position, sq('g', 1)));
    TEST_ASSERT_EQUAL_INT(PIECE_COLOR_BLACK, position.side_to_move);
    TEST_ASSERT_EQUAL_UINT8(1u, position.halfmove_clock);
    TEST_ASSERT_EQUAL_UINT16(1u, position.fullmove_number);
}

static void test_a_pawn_move_resets_the_halfmove_clock(void)
{
    const move_t knight = move_make(sq('g', 1), sq('f', 3), PIECE_TYPE_NONE, 0u);
    position_make_move(&position, &knight);
    TEST_ASSERT_EQUAL_UINT8(1u, position.halfmove_clock);

    const move_t pawn = move_make(sq('e', 7), sq('e', 6), PIECE_TYPE_NONE, 0u);
    position_make_move(&position, &pawn);
    TEST_ASSERT_EQUAL_UINT8(0u, position.halfmove_clock);
    TEST_ASSERT_EQUAL_UINT16(2u, position.fullmove_number);
}

/* The en-passant square is set only when a pawn is actually placed to take it.
 * Setting it unconditionally makes two positions that are identical to both
 * players hash differently, and fivefold repetition then never fires. */
static void test_en_passant_is_only_offered_when_it_can_be_taken(void)
{
    const move_t lone_push = move_make(sq('e', 2), sq('e', 4), PIECE_TYPE_NONE,
                                       MOVE_FLAG_DOUBLE_PAWN);
    position_make_move(&position, &lone_push);
    TEST_ASSERT_EQUAL_UINT8(SQUARE_INVALID, position.en_passant);

    position_t staged;
    TEST_ASSERT_TRUE(position_from_fen(
        &staged, "rnbqkbnr/pppp1ppp/8/8/4p3/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"));
    const move_t beside_a_pawn = move_make(sq('d', 2), sq('d', 4), PIECE_TYPE_NONE,
                                           MOVE_FLAG_DOUBLE_PAWN);
    position_make_move(&staged, &beside_a_pawn);
    TEST_ASSERT_EQUAL_UINT8(sq('d', 3), staged.en_passant);
}

static void test_castling_moves_the_rook_too(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(&board, "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"));

    const move_t kingside = move_make(sq('e', 1), sq('g', 1), PIECE_TYPE_NONE,
                                      MOVE_FLAG_CASTLE_KING);
    position_make_move(&board, &kingside);
    TEST_ASSERT_TRUE(position_piece_is(position_at(&board, sq('g', 1)), PIECE_COLOR_WHITE,
                                       PIECE_TYPE_KING));
    TEST_ASSERT_TRUE(position_piece_is(position_at(&board, sq('f', 1)), PIECE_COLOR_WHITE,
                                       PIECE_TYPE_ROOK));
    TEST_ASSERT_EQUAL_UINT8(POSITION_PIECE_NONE, position_at(&board, sq('h', 1)));
    TEST_ASSERT_EQUAL_UINT8(0u, board.castling & (POSITION_CASTLE_WHITE_KING |
                                                  POSITION_CASTLE_WHITE_QUEEN));

    position_t queenside_board;
    TEST_ASSERT_TRUE(
        position_from_fen(&queenside_board, "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"));
    const move_t queenside = move_make(sq('e', 8), sq('c', 8), PIECE_TYPE_NONE,
                                       MOVE_FLAG_CASTLE_QUEEN);
    position_make_move(&queenside_board, &queenside);
    TEST_ASSERT_TRUE(position_piece_is(position_at(&queenside_board, sq('c', 8)),
                                       PIECE_COLOR_BLACK, PIECE_TYPE_KING));
    TEST_ASSERT_TRUE(position_piece_is(position_at(&queenside_board, sq('d', 8)),
                                       PIECE_COLOR_BLACK, PIECE_TYPE_ROOK));
}

static void test_en_passant_removes_the_pawn_beside_rather_than_under(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(
        &board, "rnbqkbnr/pp1ppppp/8/2pP4/8/8/PPP1PPPP/RNBQKBNR w KQkq c6 0 3"));

    const move_t capture = move_make(sq('d', 5), sq('c', 6), PIECE_TYPE_NONE,
                                     MOVE_FLAG_CAPTURE | MOVE_FLAG_EN_PASSANT);
    position_make_move(&board, &capture);

    TEST_ASSERT_TRUE(position_piece_is(position_at(&board, sq('c', 6)), PIECE_COLOR_WHITE,
                                       PIECE_TYPE_PAWN));
    TEST_ASSERT_EQUAL_UINT8(POSITION_PIECE_NONE, position_at(&board, sq('c', 5)));
    TEST_ASSERT_EQUAL_UINT8(POSITION_PIECE_NONE, position_at(&board, sq('d', 5)));
}

static void test_promotion_places_the_chosen_piece(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(&board, "8/4P3/8/8/8/8/8/4K2k w - - 0 1"));

    const move_t promote = move_make(sq('e', 7), sq('e', 8), PIECE_TYPE_KNIGHT, 0u);
    position_make_move(&board, &promote);
    TEST_ASSERT_TRUE(position_piece_is(position_at(&board, sq('e', 8)), PIECE_COLOR_WHITE,
                                       PIECE_TYPE_KNIGHT));
}

static void test_a_captured_rook_takes_its_castling_right_with_it(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(&board, "r3k2r/8/8/8/8/8/7B/R3K2R w KQkq - 0 1"));

    const move_t takes_rook = move_make(sq('h', 2), sq('a', 8), PIECE_TYPE_NONE,
                                        MOVE_FLAG_CAPTURE);
    position_make_move(&board, &takes_rook);
    TEST_ASSERT_EQUAL_UINT8(0u, board.castling & POSITION_CASTLE_BLACK_QUEEN);
    TEST_ASSERT_NOT_EQUAL_UINT8(0u, board.castling & POSITION_CASTLE_BLACK_KING);
}

static void test_the_key_ignores_the_move_counters(void)
{
    position_t other = position;
    other.halfmove_clock = 40u;
    other.fullmove_number = 30u;
    TEST_ASSERT_EQUAL_UINT64(position_key(&position), position_key(&other));

    other.castling = 0u;
    TEST_ASSERT_NOT_EQUAL_UINT64(position_key(&position), position_key(&other));
}

static void test_fen_round_trips(void)
{
    static const char *cases[] = {
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
        "r3k2r/8/8/8/8/8/8/R3K2R b KQkq -",
        "8/8/8/8/8/8/8/4K2k w - -",
    };
    for (uint8_t index = 0u; index < 3u; index++) {
        position_t board;
        TEST_ASSERT_TRUE(position_from_fen(&board, cases[index]));
        char rendered[96];
        const uint8_t length = position_to_fen(&board, rendered, sizeof(rendered));
        TEST_ASSERT_GREATER_THAN_UINT8(0u, length);
        TEST_ASSERT_EQUAL_STRING(cases[index], rendered);
    }
}

static void test_malformed_fen_is_refused_rather_than_half_parsed(void)
{
    position_t board;
    TEST_ASSERT_FALSE(position_from_fen(&board, "not a fen"));
    TEST_ASSERT_FALSE(position_from_fen(&board, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP w - -"));
    TEST_ASSERT_FALSE(position_from_fen(&board, NULL));
}

static void test_the_diff_names_every_disagreeing_square(void)
{
    board_snapshot_t snapshot;
    board_snapshot_clear(&snapshot);
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        const position_piece_t piece = position.board[square];
        if (piece != POSITION_PIECE_NONE) {
            board_snapshot_place(&snapshot, square, position_piece_color(piece),
                                 position_piece_type(piece), 0x100u + square);
        }
    }
    TEST_ASSERT_TRUE(position_matches_snapshot(&position, &snapshot, NULL));

    /* Lift e2 and put nothing back. */
    snapshot.squares[sq('e', 2)].state = SQUARE_STATE_EMPTY;
    square_t differing[4];
    TEST_ASSERT_EQUAL_UINT8(1u, position_snapshot_diff(&position, &snapshot, differing, 4u));
    TEST_ASSERT_EQUAL_UINT8(sq('e', 2), differing[0]);

    square_t first = SQUARE_INVALID;
    TEST_ASSERT_FALSE(position_matches_snapshot(&position, &snapshot, &first));
    TEST_ASSERT_EQUAL_UINT8(sq('e', 2), first);
}

/* Not knowing is not agreeing: an unreadable square must never be reported as
 * matching, or a sensing fault quietly becomes a position. */
static void test_an_unreadable_square_never_agrees(void)
{
    board_snapshot_t snapshot;
    board_snapshot_clear(&snapshot);
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        const position_piece_t piece = position.board[square];
        if (piece != POSITION_PIECE_NONE) {
            board_snapshot_place(&snapshot, square, position_piece_color(piece),
                                 position_piece_type(piece), 0x100u + square);
        }
    }
    snapshot.squares[sq('d', 4)].state = SQUARE_STATE_UNREADABLE;
    TEST_ASSERT_FALSE(position_matches_snapshot(&position, &snapshot, NULL));
}

/* UID is not part of chess. Two identical rooks swapped is the same position. */
static void test_the_diff_ignores_which_physical_tag_is_where(void)
{
    board_snapshot_t snapshot;
    board_snapshot_clear(&snapshot);
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        const position_piece_t piece = position.board[square];
        if (piece != POSITION_PIECE_NONE) {
            board_snapshot_place(&snapshot, square, position_piece_color(piece),
                                 position_piece_type(piece), 0x100u + square);
        }
    }
    const uint64_t left = snapshot.squares[sq('a', 1)].uid;
    snapshot.squares[sq('a', 1)].uid = snapshot.squares[sq('h', 1)].uid;
    snapshot.squares[sq('h', 1)].uid = left;

    TEST_ASSERT_TRUE(position_matches_snapshot(&position, &snapshot, NULL));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_the_piece_byte_round_trips_for_every_piece);
    RUN_TEST(test_an_empty_square_has_no_colour);
    RUN_TEST(test_the_standard_start_is_where_it_should_be);
    RUN_TEST(test_king_squares_are_found);
    RUN_TEST(test_a_quiet_move_advances_the_clock_and_the_turn);
    RUN_TEST(test_a_pawn_move_resets_the_halfmove_clock);
    RUN_TEST(test_en_passant_is_only_offered_when_it_can_be_taken);
    RUN_TEST(test_castling_moves_the_rook_too);
    RUN_TEST(test_en_passant_removes_the_pawn_beside_rather_than_under);
    RUN_TEST(test_promotion_places_the_chosen_piece);
    RUN_TEST(test_a_captured_rook_takes_its_castling_right_with_it);
    RUN_TEST(test_the_key_ignores_the_move_counters);
    RUN_TEST(test_fen_round_trips);
    RUN_TEST(test_malformed_fen_is_refused_rather_than_half_parsed);
    RUN_TEST(test_the_diff_names_every_disagreeing_square);
    RUN_TEST(test_an_unreadable_square_never_agrees);
    RUN_TEST(test_the_diff_ignores_which_physical_tag_is_where);
    return UNITY_END();
}
