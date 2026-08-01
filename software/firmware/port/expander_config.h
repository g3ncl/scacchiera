#ifndef CHESSBOARD_PORT_EXPANDER_CONFIG_H
#define CHESSBOARD_PORT_EXPANDER_CONFIG_H

/* The TCA9535's direction and safe-state masks, kept apart from expander.c so
 * the host gate can assert them without ESP-IDF. They encode a boot hazard, so
 * they are tested rather than trusted: see test/test_expander_config.c. */

#include "port/board_pins.h"

#define EXPANDER_BIT(port, bit) ((port) == 0 ? (1u << (bit)) : 0u)

/* 1 is an input, 0 is an output. Port 1 is entirely inputs: only NFC_GPO1 is
 * read, and P1.3's net stops at a pullup, so leaving it an input avoids
 * driving a net that reaches nothing. */
#define EXPANDER_CONFIG_PORT_0 0xE0u
#define EXPANDER_CONFIG_PORT_1 0xFFu

/* Written while every pin is still high impedance, before the configuration
 * registers turn any of them into an output.
 *
 * At power-on both output registers hold 1111 1111. Configuring direction
 * first would make five pins drive high at once: the reader and both displays
 * would leave reset at an uncontrolled moment, the light-bar rail would switch
 * on at up to 448 mA, and SEL_RCLK would rise against its 100 k pulldown and
 * latch whatever random bits the matrix shift registers hold. Every bit below
 * is zero for that reason. */
#define EXPANDER_OUTPUT_PORT_0_SAFE 0x00u
#define EXPANDER_OUTPUT_PORT_1_SAFE 0x00u

/* The five signals the expander drives. Anything added here must also be
 * cleared in the safe masks above. */
#define EXPANDER_OUTPUT_MASK_PORT_0                                          \
    ((1u << EXP_SEL_RCLK_BIT) | (1u << EXP_NFC_RESET_N_BIT) |                \
     (1u << EXP_OLED_DC_BIT) | (1u << EXP_OLED_RESET_N_BIT) |                \
     (1u << EXP_LED_EN_BIT))

/* The three port 0 signals the expander reads. */
#define EXPANDER_INPUT_MASK_PORT_0                                           \
    ((1u << EXP_CHARGE_INPUT_FAULT_N_BIT) |                                  \
     (1u << EXP_BUTTON_N_BIT) | (1u << EXP_LED_FAULT_N_BIT))

#endif
