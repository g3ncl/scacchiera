#include "unity.h"

#include <string.h>

#include "core/move.h"

void setUp(void) {}
void tearDown(void) {}

static square_t sq(char file, uint8_t rank)
{
    return square_from_file_rank(file, rank);
}

static void test_a_move_keeps_what_it_was_given(void)
{
    const move_t move = move_make(sq('e', 2), sq('e', 4), PIECE_TYPE_NONE,
                                  MOVE_FLAG_DOUBLE_PAWN);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 2), move.from);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 4), move.to);
    TEST_ASSERT_EQUAL_INT(PIECE_TYPE_NONE, move_promotion(&move));
    TEST_ASSERT_FALSE(move_is_capture(&move));
    TEST_ASSERT_FALSE(move_is_castle(&move));
}

/* Flags are part of identity. A pawn reaching the fifth rank beside an enemy
 * pawn can be an ordinary push or an en-passant capture depending on what
 * stands there, and treating those as the same move loses a piece. */
static void test_moves_that_differ_only_in_flags_are_different_moves(void)
{
    const move_t quiet = move_make(sq('d', 5), sq('c', 6), PIECE_TYPE_NONE, 0u);
    const move_t passant = move_make(sq('d', 5), sq('c', 6), PIECE_TYPE_NONE,
                                     MOVE_FLAG_CAPTURE | MOVE_FLAG_EN_PASSANT);
    TEST_ASSERT_FALSE(move_equal(&quiet, &passant));
}

static void test_promotions_to_different_pieces_are_different_moves(void)
{
    const move_t queen = move_make(sq('e', 7), sq('e', 8), PIECE_TYPE_QUEEN, 0u);
    const move_t knight = move_make(sq('e', 7), sq('e', 8), PIECE_TYPE_KNIGHT, 0u);
    TEST_ASSERT_FALSE(move_equal(&queen, &knight));
    TEST_ASSERT_TRUE(move_equal(&queen, &queen));
}

/* Null has to be distinguishable from a1a1, which is also not a legal move but
 * is a different thing to say. */
static void test_null_is_not_a_square(void)
{
    const move_t null = move_null();
    TEST_ASSERT_TRUE(move_is_null(&null));

    const move_t a1a1 = move_make(0u, 0u, PIECE_TYPE_NONE, 0u);
    TEST_ASSERT_FALSE(move_is_null(&a1a1));
}

static void test_castle_flags_are_recognised(void)
{
    const move_t kingside = move_make(sq('e', 1), sq('g', 1), PIECE_TYPE_NONE,
                                      MOVE_FLAG_CASTLE_KING);
    const move_t queenside = move_make(sq('e', 8), sq('c', 8), PIECE_TYPE_NONE,
                                       MOVE_FLAG_CASTLE_QUEEN);
    TEST_ASSERT_TRUE(move_is_castle(&kingside));
    TEST_ASSERT_TRUE(move_is_castle(&queenside));
}

static void test_text_form(void)
{
    char text[8];

    const move_t quiet = move_make(sq('e', 2), sq('e', 4), PIECE_TYPE_NONE, 0u);
    TEST_ASSERT_EQUAL_UINT8(4u, move_to_text(&quiet, text, sizeof(text)));
    TEST_ASSERT_EQUAL_STRING("e2e4", text);

    const move_t promotion = move_make(sq('e', 7), sq('e', 8), PIECE_TYPE_QUEEN, 0u);
    TEST_ASSERT_EQUAL_UINT8(5u, move_to_text(&promotion, text, sizeof(text)));
    TEST_ASSERT_EQUAL_STRING("e7e8q", text);

    const move_t null = move_null();
    TEST_ASSERT_EQUAL_UINT8(0u, move_to_text(&null, text, sizeof(text)));
    TEST_ASSERT_EQUAL_UINT8(0u, move_to_text(&quiet, text, 3u));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_a_move_keeps_what_it_was_given);
    RUN_TEST(test_moves_that_differ_only_in_flags_are_different_moves);
    RUN_TEST(test_promotions_to_different_pieces_are_different_moves);
    RUN_TEST(test_null_is_not_a_square);
    RUN_TEST(test_castle_flags_are_recognised);
    RUN_TEST(test_text_form);
    return UNITY_END();
}
