#include "unity.h"

#include "port/expander_config.h"

void setUp(void) {}
void tearDown(void) {}

/* The expander's masks encode a boot hazard. At power-on the TCA9535 holds
 * 1111 1111 in both output registers, so any pin made an output before its
 * value is written drives high: the reader and both displays leave reset
 * uncontrolled, the light-bar rail switches on, and SEL_RCLK rises against its
 * pulldown and latches random matrix selection. These tests keep the masks
 * honest without a board. */

static void test_direction_mask_matches_the_signal_lists(void)
{
    /* A 0 in the configuration register is an output. */
    const unsigned outputs = (unsigned)(~EXPANDER_CONFIG_PORT_0) & 0xFFu;
    TEST_ASSERT_EQUAL_HEX8(EXPANDER_OUTPUT_MASK_PORT_0, outputs);

    const unsigned inputs = EXPANDER_CONFIG_PORT_0 & 0xFFu;
    TEST_ASSERT_EQUAL_HEX8(EXPANDER_INPUT_MASK_PORT_0, inputs);
}

static void test_no_bit_is_both_input_and_output(void)
{
    TEST_ASSERT_EQUAL_HEX8(0u,
        EXPANDER_OUTPUT_MASK_PORT_0 & EXPANDER_INPUT_MASK_PORT_0);
}

static void test_every_port_0_bit_is_accounted_for(void)
{
    TEST_ASSERT_EQUAL_HEX8(0xFFu,
        EXPANDER_OUTPUT_MASK_PORT_0 | EXPANDER_INPUT_MASK_PORT_0);
}

/* The one that matters. Every driven pin must come up in its inactive state,
 * and for all five of these that state is low. */
static void test_every_output_starts_low(void)
{
    TEST_ASSERT_EQUAL_HEX8(0u,
        EXPANDER_OUTPUT_PORT_0_SAFE & EXPANDER_OUTPUT_MASK_PORT_0);
}

static void test_the_resets_and_the_rail_are_asserted_at_boot(void)
{
    /* Named individually so a failure says which one, rather than only that a
     * mask changed. RESET_N low is in reset; LED_EN low is the rail off. */
    TEST_ASSERT_EQUAL_HEX8(0u, EXPANDER_OUTPUT_PORT_0_SAFE & (1u << EXP_NFC_RESET_N_BIT));
    TEST_ASSERT_EQUAL_HEX8(0u, EXPANDER_OUTPUT_PORT_0_SAFE & (1u << EXP_OLED_RESET_N_BIT));
    TEST_ASSERT_EQUAL_HEX8(0u, EXPANDER_OUTPUT_PORT_0_SAFE & (1u << EXP_LED_EN_BIT));
    TEST_ASSERT_EQUAL_HEX8(0u, EXPANDER_OUTPUT_PORT_0_SAFE & (1u << EXP_SEL_RCLK_BIT));
}

/* Port 1 drives nothing, so it must be all inputs. P1.3's net stops at a
 * pullup and driving it would be driving a wire that reaches nothing. */
static void test_port_1_drives_nothing(void)
{
    TEST_ASSERT_EQUAL_HEX8(0xFFu, EXPANDER_CONFIG_PORT_1);
    TEST_ASSERT_EQUAL_HEX8(0x00u, EXPANDER_OUTPUT_PORT_1_SAFE);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_direction_mask_matches_the_signal_lists);
    RUN_TEST(test_no_bit_is_both_input_and_output);
    RUN_TEST(test_every_port_0_bit_is_accounted_for);
    RUN_TEST(test_every_output_starts_low);
    RUN_TEST(test_the_resets_and_the_rail_are_asserted_at_boot);
    RUN_TEST(test_port_1_drives_nothing);
    return UNITY_END();
}
