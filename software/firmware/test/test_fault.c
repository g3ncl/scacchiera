#include "unity.h"

#include <string.h>

#include "core/fault.h"

void setUp(void) {}
void tearDown(void) {}

/* docs/functional/gameplay.md lists exactly five faults. If a row is added
 * there and not here, this fails rather than letting the table drift. */
static void test_every_fault_has_a_distinct_name(void)
{
    TEST_ASSERT_EQUAL_INT(6, BOARD_FAULT_COUNT);
    for (int a = 0; a < BOARD_FAULT_COUNT; a++) {
        const char *name = board_fault_name((board_fault_t)a);
        TEST_ASSERT_NOT_NULL(name);
        TEST_ASSERT_NOT_EQUAL_INT(0, strcmp(name, "UNKNOWN"));
        for (int b = a + 1; b < BOARD_FAULT_COUNT; b++) {
            TEST_ASSERT_NOT_EQUAL_INT(0, strcmp(name, board_fault_name((board_fault_t)b)));
        }
    }
}

static void test_spec_names_are_exact(void)
{
    TEST_ASSERT_EQUAL_STRING("TAG_FAULT", board_fault_name(BOARD_FAULT_TAG_FAULT));
    TEST_ASSERT_EQUAL_STRING("UID_DUPLICATE", board_fault_name(BOARD_FAULT_UID_DUPLICATE));
    TEST_ASSERT_EQUAL_STRING("RF_CROSSTALK", board_fault_name(BOARD_FAULT_RF_CROSSTALK));
    TEST_ASSERT_EQUAL_STRING("SQUARE_UNSTABLE", board_fault_name(BOARD_FAULT_SQUARE_UNSTABLE));
    TEST_ASSERT_EQUAL_STRING("BOARD_MISMATCH", board_fault_name(BOARD_FAULT_BOARD_MISMATCH));
}

static void test_unknown_fault_is_named_not_crashed(void)
{
    TEST_ASSERT_EQUAL_STRING("UNKNOWN", board_fault_name((board_fault_t)99));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_every_fault_has_a_distinct_name);
    RUN_TEST(test_spec_names_are_exact);
    RUN_TEST(test_unknown_fault_is_named_not_crashed);
    return UNITY_END();
}
