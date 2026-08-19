#include "unity.h"

#include "core/button.h"

static button_t button;

void setUp(void)
{
    button_init(&button);
}

void tearDown(void) {}

static void test_a_short_press_fires_on_release(void)
{
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_NONE, button_update(&button, true, 1000u));
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_NONE, button_update(&button, true, 1200u));
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_SHORT, button_update(&button, false, 1400u));
}

static void test_a_long_hold_fires_while_still_held(void)
{
    (void)button_update(&button, true, 1000u);
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_NONE, button_update(&button, true, 3999u));
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_LONG, button_update(&button, true, 4000u));
    /* Once. Holding longer is not more gestures. */
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_NONE, button_update(&button, true, 9000u));
    /* And the release of a consumed hold is not a short press. */
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_NONE, button_update(&button, false, 9200u));
}

static void test_idle_reports_nothing(void)
{
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_NONE, button_update(&button, false, 1000u));
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_NONE, button_update(&button, false, 2000u));
}

static void test_the_millisecond_wrap_is_a_non_event(void)
{
    (void)button_update(&button, true, 0xFFFFFC00u);
    TEST_ASSERT_EQUAL_INT(BUTTON_EVENT_LONG, button_update(&button, true, 2000u));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_a_short_press_fires_on_release);
    RUN_TEST(test_a_long_hold_fires_while_still_held);
    RUN_TEST(test_idle_reports_nothing);
    RUN_TEST(test_the_millisecond_wrap_is_a_non_event);
    return UNITY_END();
}
