#include "unity.h"

#include "core/snapshot.h"

static board_snapshot_t a;
static board_snapshot_t b;

void setUp(void)
{
    board_snapshot_clear(&a);
    board_snapshot_clear(&b);
}

void tearDown(void) {}

static void test_cleared_snapshot_is_empty_and_faultless(void)
{
    TEST_ASSERT_EQUAL_UINT8(0u, board_snapshot_occupied_count(&a));
    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, a.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(SQUARE_INVALID, a.fault.square);
    for (square_t square = 0; square < BOARD_SQUARES; square++) {
        TEST_ASSERT_EQUAL_INT(SQUARE_STATE_EMPTY, a.squares[square].state);
    }
}

static void test_place_marks_one_square(void)
{
    const square_t e2 = square_from_file_rank('e', 2);
    board_snapshot_place(&a, e2, PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 0x1122334455667788u);
    TEST_ASSERT_EQUAL_UINT8(1u, board_snapshot_occupied_count(&a));
    TEST_ASSERT_EQUAL_INT(SQUARE_STATE_OCCUPIED, a.squares[e2].state);
    TEST_ASSERT_EQUAL_INT(PIECE_TYPE_PAWN, a.squares[e2].type);
    TEST_ASSERT_EQUAL_HEX64(0x1122334455667788u, a.squares[e2].uid);
}

static void test_place_on_invalid_square_is_ignored(void)
{
    board_snapshot_place(&a, SQUARE_INVALID, PIECE_COLOR_WHITE, PIECE_TYPE_KING, 1u);
    TEST_ASSERT_EQUAL_UINT8(0u, board_snapshot_occupied_count(&a));
}

static void test_equality_ignores_stale_bytes_on_empty_squares(void)
{
    /* An empty square carries whatever colour and type happen to be in the
     * struct. Two positions that are the same must not differ over that. */
    a.squares[0].color = PIECE_COLOR_BLACK;
    a.squares[0].type = PIECE_TYPE_QUEEN;
    a.squares[0].uid = 0xDEADBEEFu;
    TEST_ASSERT_TRUE(board_snapshot_equal(&a, &b));
}

static void test_equality_detects_a_moved_piece(void)
{
    const square_t e2 = square_from_file_rank('e', 2);
    const square_t e4 = square_from_file_rank('e', 4);
    board_snapshot_place(&a, e2, PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 7u);
    board_snapshot_place(&b, e4, PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 7u);
    TEST_ASSERT_FALSE(board_snapshot_equal(&a, &b));
}

static void test_equality_detects_a_swapped_uid(void)
{
    const square_t e2 = square_from_file_rank('e', 2);
    board_snapshot_place(&a, e2, PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 7u);
    board_snapshot_place(&b, e2, PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 8u);
    TEST_ASSERT_FALSE(board_snapshot_equal(&a, &b));
}

static void test_unreadable_is_not_empty(void)
{
    a.squares[0].state = SQUARE_STATE_UNREADABLE;
    TEST_ASSERT_FALSE(board_snapshot_equal(&a, &b));
    TEST_ASSERT_EQUAL_UINT8(0u, board_snapshot_occupied_count(&a));
}

static void test_duplicate_uid_is_found(void)
{
    const square_t a1 = square_from_file_rank('a', 1);
    const square_t h8 = square_from_file_rank('h', 8);
    board_snapshot_place(&a, a1, PIECE_COLOR_WHITE, PIECE_TYPE_ROOK, 0x42u);
    board_snapshot_place(&a, h8, PIECE_COLOR_BLACK, PIECE_TYPE_ROOK, 0x42u);
    square_t first = SQUARE_INVALID;
    square_t second = SQUARE_INVALID;
    TEST_ASSERT_TRUE(board_snapshot_find_duplicate_uid(&a, &first, &second));
    TEST_ASSERT_EQUAL_UINT8(a1, first);
    TEST_ASSERT_EQUAL_UINT8(h8, second);
}

static void test_unique_uids_report_no_duplicate(void)
{
    for (square_t square = 0; square < 32u; square++) {
        board_snapshot_place(&a, square, PIECE_COLOR_WHITE, PIECE_TYPE_PAWN,
                             (uint64_t)square + 1u);
    }
    square_t first = 1u;
    square_t second = 2u;
    TEST_ASSERT_FALSE(board_snapshot_find_duplicate_uid(&a, &first, &second));
    /* Outputs must be untouched on the negative path. */
    TEST_ASSERT_EQUAL_UINT8(1u, first);
    TEST_ASSERT_EQUAL_UINT8(2u, second);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_cleared_snapshot_is_empty_and_faultless);
    RUN_TEST(test_place_marks_one_square);
    RUN_TEST(test_place_on_invalid_square_is_ignored);
    RUN_TEST(test_equality_ignores_stale_bytes_on_empty_squares);
    RUN_TEST(test_equality_detects_a_moved_piece);
    RUN_TEST(test_equality_detects_a_swapped_uid);
    RUN_TEST(test_unreadable_is_not_empty);
    RUN_TEST(test_duplicate_uid_is_found);
    RUN_TEST(test_unique_uids_report_no_duplicate);
    return UNITY_END();
}
