#ifndef CHESSBOARD_CORE_CHESSCLOCK_H
#define CHESSBOARD_CORE_CHESSCLOCK_H

#include <stdbool.h>
#include <stdint.h>

#include "core/piece.h"
#include "core/square.h"

/* The game clock.
 *
 * Named chessclock rather than clock so an include can never be confused with
 * core/hw/clock.h, which is the monotonic millisecond source this runs on.
 * Nothing here reads that source itself: the time arrives as a parameter, which
 * is what lets a test run a ninety minute game instantly. */

#define TIME_PRESET_COUNT 4
#define TIME_PRESET_NONE 0xFFu

typedef struct {
    /* Upper case: the 5x7 font has no lower case glyphs. */
    const char *name;
    uint32_t initial_ms;
    uint32_t increment_ms;
} time_preset_t;

/* The four presets, in the order of the squares the white king is held on:
 * d4, d5, e4, e5.
 *
 * These values are defaults, not requirements. docs/functional/gameplay.md
 * specifies the gesture and says nothing about what it selects, so the owner
 * is expected to replace them; every test asserts the mechanism and none
 * asserts a number. A zero increment is a sudden-death control. */
extern const time_preset_t TIME_PRESETS[TIME_PRESET_COUNT];

/* The square that selects preset `index`, or SQUARE_INVALID. */
square_t time_preset_square(uint8_t index);
/* The preset a square selects, or TIME_PRESET_NONE. */
uint8_t time_preset_for_square(square_t square);

typedef struct {
    uint32_t remaining_ms[2];
    uint32_t increment_ms[2];
    piece_color_t running;
    bool has_time_control;
    bool paused;
    bool flagged[2];
    /* The instant remaining_ms was last brought up to date. Every calculation
     * is a delta against this, so the 49.7 day wrap of the millisecond source
     * is a non-event. */
    uint32_t charged_to_ms;
} chessclock_t;

void chessclock_init_untimed(chessclock_t *clock);
void chessclock_init_preset(chessclock_t *clock, uint8_t preset, piece_color_t first,
                            uint32_t now_ms);

/* Charges elapsed time to whichever side is running. Safe to call at any rate,
 * including twice with the same reading. */
void chessclock_tick(chessclock_t *clock, uint32_t now_ms);

/* Hands the turn over, charging the outgoing side first. */
void chessclock_switch(chessclock_t *clock, uint32_t now_ms);

/* Credited at commitment rather than at placement, so a provisional move that
 * is taken back needs no reversal. The visible cost is that the increment
 * appears one lift late. */
void chessclock_credit_increment(chessclock_t *clock, piece_color_t side);

void chessclock_pause(chessclock_t *clock, uint32_t now_ms);
void chessclock_resume(chessclock_t *clock, uint32_t now_ms);
bool chessclock_is_paused(const chessclock_t *clock);

bool chessclock_flagged(const chessclock_t *clock, piece_color_t *side);
uint32_t chessclock_remaining_ms(const chessclock_t *clock, piece_color_t side);

/* "10:00", or "0:09.4" under ten seconds where tenths start to matter.
 * Returns the length written, or 0 when the buffer is too small. */
uint8_t chessclock_format(const chessclock_t *clock, piece_color_t side, char *out,
                          uint8_t capacity);

#endif
