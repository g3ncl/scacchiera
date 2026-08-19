#include "unity.h"

#include <stdio.h>
#include <string.h>

#include "core/movegen.h"

/* Perft is the only test that meaningfully proves a move generator. It counts
 * the leaves of the legal move tree to a given depth, so a single wrong rule
 * anywhere shows up as a wrong total, and the totals for these positions are
 * published and independently agreed.
 *
 * The positions are the standard set. Each was chosen by its author to break a
 * different rule: Kiwipete covers castling and pins, position 3 covers
 * promotion and en passant near the edge, position 4 covers promotion with
 * check, position 5 covers castling rights being lost.
 *
 * Depths are kept where the whole file runs in a few seconds, because this is
 * in `make check` and a gate nobody waits for is a gate nobody runs. Raising
 * MAX_DEPTH is how to go deeper by hand. */

#define MAX_DEPTH 6

static move_list_t lists[MAX_DEPTH];
static position_t stack[MAX_DEPTH];

void setUp(void) {}
void tearDown(void) {}

static uint64_t perft(const position_t *position, uint8_t depth)
{
    if (depth == 0u) {
        return 1u;
    }
    move_list_t *list = &lists[depth - 1u];
    movegen_legal(position, list);

    if (depth == 1u) {
        return (uint64_t)list->count;
    }

    uint64_t nodes = 0u;
    const uint8_t count = list->count;
    /* The list is reused by the recursion below, so the moves are copied out
     * before descending. */
    move_t moves[MOVEGEN_MAX_MOVES];
    memcpy(moves, list->moves, sizeof(move_t) * count);

    for (uint8_t index = 0u; index < count; index++) {
        stack[depth - 1u] = *position;
        position_make_move(&stack[depth - 1u], &moves[index]);
        nodes += perft(&stack[depth - 1u], (uint8_t)(depth - 1u));
    }
    return nodes;
}

static void expect_perft(const char *fen, uint8_t depth, uint64_t expected)
{
    position_t position;
    TEST_ASSERT_TRUE_MESSAGE(position_from_fen(&position, fen), fen);

    const uint64_t nodes = perft(&position, depth);
    if (nodes != expected) {
        char message[160];
        (void)snprintf(message, sizeof(message), "perft(%u) on %s: got %llu want %llu",
                       (unsigned)depth, fen, (unsigned long long)nodes,
                       (unsigned long long)expected);
        TEST_FAIL_MESSAGE(message);
    }
}

#define START_FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
#define KIWIPETE_FEN \
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
#define POSITION_3_FEN "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"
#define POSITION_4_FEN \
    "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"
#define POSITION_5_FEN "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"

static void test_perft_from_the_standard_start(void)
{
    expect_perft(START_FEN, 1u, 20u);
    expect_perft(START_FEN, 2u, 400u);
    expect_perft(START_FEN, 3u, 8902u);
    expect_perft(START_FEN, 4u, 197281u);
}

static void test_perft_kiwipete(void)
{
    expect_perft(KIWIPETE_FEN, 1u, 48u);
    expect_perft(KIWIPETE_FEN, 2u, 2039u);
    expect_perft(KIWIPETE_FEN, 3u, 97862u);
}

static void test_perft_position_three(void)
{
    expect_perft(POSITION_3_FEN, 1u, 14u);
    expect_perft(POSITION_3_FEN, 2u, 191u);
    expect_perft(POSITION_3_FEN, 3u, 2812u);
    expect_perft(POSITION_3_FEN, 4u, 43238u);
}

static void test_perft_position_four(void)
{
    expect_perft(POSITION_4_FEN, 1u, 6u);
    expect_perft(POSITION_4_FEN, 2u, 264u);
    expect_perft(POSITION_4_FEN, 3u, 9467u);
}

static void test_perft_position_five(void)
{
    expect_perft(POSITION_5_FEN, 1u, 44u);
    expect_perft(POSITION_5_FEN, 2u, 1486u);
    expect_perft(POSITION_5_FEN, 3u, 62379u);
}

/* The padded board is pure arithmetic, so it is checked against the arithmetic
 * rather than trusted as a literal. A transposed index here is not a compile
 * error, it is a board that plays a different game, which is the same reason
 * test_matrix_encoding.c pins the selection map. */
static uint8_t knight_moves_from(char file, uint8_t rank)
{
    position_t board;
    position_clear(&board);
    const square_t knight = square_from_file_rank(file, rank);
    board.board[knight] = position_piece_make(PIECE_COLOR_WHITE, PIECE_TYPE_KNIGHT);
    /* Kings placed far away so nothing here is about check. */
    board.board[square_from_file_rank('a', 8)] =
        position_piece_make(PIECE_COLOR_WHITE, PIECE_TYPE_KING);
    board.board[square_from_file_rank('h', 1)] =
        position_piece_make(PIECE_COLOR_BLACK, PIECE_TYPE_KING);

    move_list_t list;
    movegen_legal(&board, &list);
    uint8_t count = 0u;
    for (uint8_t index = 0u; index < list.count; index++) {
        if (list.moves[index].from == knight) {
            count++;
        }
    }
    return count;
}

static void test_the_padded_index_tables_agree_with_the_arithmetic(void)
{
    /* A lone knight has exactly two moves from a corner, three from beside it,
     * four from an edge and eight from the middle. Those counts hold only if
     * the padding stops a jump wrapping onto the far file, which is the one
     * job these tables have. */
    TEST_ASSERT_EQUAL_UINT8(2u, knight_moves_from('a', 1));
    TEST_ASSERT_EQUAL_UINT8(2u, knight_moves_from('h', 8));
    TEST_ASSERT_EQUAL_UINT8(3u, knight_moves_from('b', 1));
    TEST_ASSERT_EQUAL_UINT8(4u, knight_moves_from('a', 4));
    TEST_ASSERT_EQUAL_UINT8(8u, knight_moves_from('d', 4));
    TEST_ASSERT_EQUAL_UINT8(8u, knight_moves_from('e', 5));
}

static void test_a_king_may_not_step_into_check(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(&board, "8/8/8/8/8/8/5k2/4K2r w - - 0 1"));

    move_list_t list;
    movegen_legal(&board, &list);
    for (uint8_t index = 0u; index < list.count; index++) {
        TEST_ASSERT_NOT_EQUAL_UINT8(square_from_file_rank('f', 1), list.moves[index].to);
        TEST_ASSERT_NOT_EQUAL_UINT8(square_from_file_rank('d', 1), list.moves[index].to);
    }
}

static void test_a_pinned_piece_may_not_leave_the_pin(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(&board, "7k/8/8/8/4r3/8/4N3/4K3 w - - 0 1"));

    move_list_t list;
    movegen_legal(&board, &list);
    for (uint8_t index = 0u; index < list.count; index++) {
        TEST_ASSERT_NOT_EQUAL_UINT8(square_from_file_rank('e', 2), list.moves[index].from);
    }
}

/* The case a pin-aware generator gets wrong and make-and-test gets right: the
 * capture removes two pawns from the rank at once and exposes the king. */
static void test_en_passant_that_would_discover_check_is_refused(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(&board, "8/8/8/K2pP2r/8/8/8/7k w - d6 0 1"));

    move_list_t list;
    movegen_legal(&board, &list);
    for (uint8_t index = 0u; index < list.count; index++) {
        TEST_ASSERT_EQUAL_UINT8(0u, list.moves[index].flags & MOVE_FLAG_EN_PASSANT);
    }
}

static void test_castling_is_refused_through_and_into_check(void)
{
    position_t through;
    TEST_ASSERT_TRUE(position_from_fen(&through, "4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"));
    move_list_t list;
    movegen_legal(&through, &list);
    uint8_t castles = 0u;
    for (uint8_t index = 0u; index < list.count; index++) {
        if (move_is_castle(&list.moves[index])) {
            castles++;
        }
    }
    TEST_ASSERT_EQUAL_UINT8(2u, castles);

    /* A rook covering f1 stops the kingside castle only. */
    position_t covered;
    TEST_ASSERT_TRUE(position_from_fen(&covered, "5r2/8/8/8/8/8/8/R3K2R w KQ - 0 1"));
    movegen_legal(&covered, &list);
    castles = 0u;
    for (uint8_t index = 0u; index < list.count; index++) {
        if (move_is_castle(&list.moves[index])) {
            castles++;
            TEST_ASSERT_EQUAL_UINT8(MOVE_FLAG_CASTLE_QUEEN, list.moves[index].flags);
        }
    }
    TEST_ASSERT_EQUAL_UINT8(1u, castles);
}

static void test_castling_is_refused_out_of_check(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(&board, "4r3/8/8/8/8/8/8/R3K2R w KQ - 0 1"));
    move_list_t list;
    movegen_legal(&board, &list);
    for (uint8_t index = 0u; index < list.count; index++) {
        TEST_ASSERT_FALSE(move_is_castle(&list.moves[index]));
    }
}

static void test_every_promotion_choice_is_a_separate_move(void)
{
    position_t board;
    TEST_ASSERT_TRUE(position_from_fen(&board, "8/4P3/8/8/8/8/8/4K2k w - - 0 1"));

    move_list_t list;
    movegen_legal(&board, &list);
    uint8_t promotions = 0u;
    for (uint8_t index = 0u; index < list.count; index++) {
        if (move_promotion(&list.moves[index]) != PIECE_TYPE_NONE) {
            promotions++;
        }
    }
    TEST_ASSERT_EQUAL_UINT8(4u, promotions);
}

static void test_mate_and_stalemate_generate_nothing(void)
{
    position_t mate;
    TEST_ASSERT_TRUE(position_from_fen(&mate, "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"));
    move_list_t list;
    movegen_legal(&mate, &list);
    TEST_ASSERT_EQUAL_UINT8(0u, list.count);
    TEST_ASSERT_TRUE(movegen_in_check(&mate, PIECE_COLOR_WHITE));

    position_t stalemate;
    TEST_ASSERT_TRUE(position_from_fen(&stalemate, "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1"));
    movegen_legal(&stalemate, &list);
    TEST_ASSERT_EQUAL_UINT8(0u, list.count);
    TEST_ASSERT_FALSE(movegen_in_check(&stalemate, PIECE_COLOR_BLACK));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_the_padded_index_tables_agree_with_the_arithmetic);
    RUN_TEST(test_a_king_may_not_step_into_check);
    RUN_TEST(test_a_pinned_piece_may_not_leave_the_pin);
    RUN_TEST(test_en_passant_that_would_discover_check_is_refused);
    RUN_TEST(test_castling_is_refused_through_and_into_check);
    RUN_TEST(test_castling_is_refused_out_of_check);
    RUN_TEST(test_every_promotion_choice_is_a_separate_move);
    RUN_TEST(test_mate_and_stalemate_generate_nothing);
    RUN_TEST(test_perft_from_the_standard_start);
    RUN_TEST(test_perft_kiwipete);
    RUN_TEST(test_perft_position_three);
    RUN_TEST(test_perft_position_four);
    RUN_TEST(test_perft_position_five);
    return UNITY_END();
}
