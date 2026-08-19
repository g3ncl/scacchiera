#include "core/chessclock.h"

#include <string.h>

#define MS_PER_SECOND 1000u
#define MS_PER_MINUTE 60000u
/* Below this the display switches to tenths, because at a few seconds the
 * difference between 3 and 4 is the whole decision a player is making. */
#define TENTHS_BELOW_MS 10000u

const time_preset_t TIME_PRESETS[TIME_PRESET_COUNT] = {
    {"3+2", 3u * MS_PER_MINUTE, 2u * MS_PER_SECOND},
    {"5+3", 5u * MS_PER_MINUTE, 3u * MS_PER_SECOND},
    {"10+5", 10u * MS_PER_MINUTE, 5u * MS_PER_SECOND},
    {"25+0", 25u * MS_PER_MINUTE, 0u},
};

/* d4, d5, e4, e5, matching the order above. */
static const char PRESET_FILES[TIME_PRESET_COUNT] = {'d', 'd', 'e', 'e'};
static const uint8_t PRESET_RANKS[TIME_PRESET_COUNT] = {4u, 5u, 4u, 5u};

square_t time_preset_square(uint8_t index)
{
    if (index >= TIME_PRESET_COUNT) {
        return SQUARE_INVALID;
    }
    return square_from_file_rank(PRESET_FILES[index], PRESET_RANKS[index]);
}

uint8_t time_preset_for_square(square_t square)
{
    for (uint8_t index = 0u; index < TIME_PRESET_COUNT; index++) {
        if (time_preset_square(index) == square) {
            return index;
        }
    }
    return TIME_PRESET_NONE;
}

void chessclock_init_untimed(chessclock_t *clock)
{
    memset(clock, 0, sizeof(*clock));
    clock->running = PIECE_COLOR_WHITE;
}

void chessclock_init_preset(chessclock_t *clock, uint8_t preset, piece_color_t first,
                            uint32_t now_ms)
{
    chessclock_init_untimed(clock);
    if (preset >= TIME_PRESET_COUNT) {
        return;
    }
    clock->has_time_control = true;
    clock->running = first;
    clock->charged_to_ms = now_ms;
    for (uint8_t side = 0u; side < 2u; side++) {
        clock->remaining_ms[side] = TIME_PRESETS[preset].initial_ms;
        clock->increment_ms[side] = TIME_PRESETS[preset].increment_ms;
    }
}

void chessclock_tick(chessclock_t *clock, uint32_t now_ms)
{
    if (!clock->has_time_control || clock->paused) {
        return;
    }
    const uint32_t elapsed = now_ms - clock->charged_to_ms;
    clock->charged_to_ms = now_ms;
    if (elapsed == 0u) {
        return;
    }

    const uint8_t side = (uint8_t)clock->running;
    if (clock->flagged[side]) {
        return;
    }
    if (elapsed >= clock->remaining_ms[side]) {
        clock->remaining_ms[side] = 0u;
        clock->flagged[side] = true;
    } else {
        clock->remaining_ms[side] -= elapsed;
    }
}

void chessclock_switch(chessclock_t *clock, uint32_t now_ms)
{
    if (!clock->has_time_control) {
        return;
    }
    chessclock_tick(clock, now_ms);
    clock->running = (clock->running == PIECE_COLOR_WHITE) ? PIECE_COLOR_BLACK
                                                           : PIECE_COLOR_WHITE;
    clock->charged_to_ms = now_ms;
}

void chessclock_credit_increment(chessclock_t *clock, piece_color_t side)
{
    if (!clock->has_time_control || clock->flagged[(uint8_t)side]) {
        return;
    }
    clock->remaining_ms[(uint8_t)side] += clock->increment_ms[(uint8_t)side];
}

void chessclock_pause(chessclock_t *clock, uint32_t now_ms)
{
    if (!clock->has_time_control || clock->paused) {
        return;
    }
    chessclock_tick(clock, now_ms);
    clock->paused = true;
}

void chessclock_resume(chessclock_t *clock, uint32_t now_ms)
{
    if (!clock->has_time_control || !clock->paused) {
        return;
    }
    clock->paused = false;
    /* Rebased rather than backdated, so the paused interval is never charged
     * to anyone. */
    clock->charged_to_ms = now_ms;
}

bool chessclock_is_paused(const chessclock_t *clock)
{
    return clock->paused;
}

bool chessclock_flagged(const chessclock_t *clock, piece_color_t *side)
{
    for (uint8_t index = 0u; index < 2u; index++) {
        if (clock->flagged[index]) {
            if (side != NULL) {
                *side = (piece_color_t)index;
            }
            return true;
        }
    }
    return false;
}

uint32_t chessclock_remaining_ms(const chessclock_t *clock, piece_color_t side)
{
    return clock->remaining_ms[(uint8_t)side];
}

uint8_t chessclock_format(const chessclock_t *clock, piece_color_t side, char *out,
                          uint8_t capacity)
{
    if (out == NULL || capacity < 8) {
        return 0u;
    }
    const uint32_t remaining = clock->remaining_ms[(uint8_t)side];
    uint8_t length = 0u;

    if (remaining < TENTHS_BELOW_MS) {
        const uint32_t seconds = remaining / MS_PER_SECOND;
        const uint32_t tenths = (remaining % MS_PER_SECOND) / 100u;
        out[length++] = '0';
        out[length++] = ':';
        out[length++] = '0';
        out[length++] = (char)('0' + seconds);
        out[length++] = '.';
        out[length++] = (char)('0' + tenths);
        out[length] = '\0';
        return length;
    }

    const uint32_t total_seconds = remaining / MS_PER_SECOND;
    const uint32_t minutes = total_seconds / 60u;
    const uint32_t seconds = total_seconds % 60u;

    if (minutes >= 100u) {
        out[length++] = (char)('0' + ((minutes / 100u) % 10u));
    }
    if (minutes >= 10u) {
        out[length++] = (char)('0' + ((minutes / 10u) % 10u));
    }
    out[length++] = (char)('0' + (minutes % 10u));
    out[length++] = ':';
    out[length++] = (char)('0' + (seconds / 10u));
    out[length++] = (char)('0' + (seconds % 10u));
    out[length] = '\0';
    return length;
}
