#include "unity.h"

#include "core/square.h"

void setUp(void) {}
void tearDown(void) {}

static void test_a1_is_zero(void)
{
    TEST_ASSERT_EQUAL_UINT8(0u, square_from_file_rank('a', 1));
}

static void test_h8_is_last(void)
{
    TEST_ASSERT_EQUAL_UINT8(BOARD_SQUARES - 1u, square_from_file_rank('h', 8));
}

static void test_indices_are_unique_and_dense(void)
{
    bool seen[BOARD_SQUARES] = {false};
    for (uint8_t rank = 1u; rank <= BOARD_RANKS; rank++) {
        for (char file = 'a'; file <= 'h'; file++) {
            const square_t square = square_from_file_rank(file, rank);
            TEST_ASSERT_TRUE(square_is_valid(square));
            TEST_ASSERT_FALSE(seen[square]);
            seen[square] = true;
        }
    }
    for (square_t square = 0; square < BOARD_SQUARES; square++) {
        TEST_ASSERT_TRUE(seen[square]);
    }
}

static void test_round_trip(void)
{
    for (square_t square = 0; square < BOARD_SQUARES; square++) {
        const char file = square_file_letter(square);
        const uint8_t rank = square_rank(square);
        TEST_ASSERT_EQUAL_UINT8(square, square_from_file_rank(file, rank));
    }
}

static void test_out_of_range_rejected(void)
{
    TEST_ASSERT_EQUAL_UINT8(SQUARE_INVALID, square_from_file_rank('i', 1));
    TEST_ASSERT_EQUAL_UINT8(SQUARE_INVALID, square_from_file_rank('`', 1));
    TEST_ASSERT_EQUAL_UINT8(SQUARE_INVALID, square_from_file_rank('a', 0));
    TEST_ASSERT_EQUAL_UINT8(SQUARE_INVALID, square_from_file_rank('a', 9));
    TEST_ASSERT_FALSE(square_is_valid(SQUARE_INVALID));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_a1_is_zero);
    RUN_TEST(test_h8_is_last);
    RUN_TEST(test_indices_are_unique_and_dense);
    RUN_TEST(test_round_trip);
    RUN_TEST(test_out_of_range_rejected);
    return UNITY_END();
}
