#ifndef CHESSBOARD_CORE_HW_OUTPUT_H
#define CHESSBOARD_CORE_HW_OUTPUT_H

#include <stdint.h>

#include "core/piece.h"

/* The two player surfaces from docs/functional/interface.md: display text and
 * brief light-bar cues. Kept as one interface because core/ only ever needs to
 * say what to communicate, never how a given rail renders it. */

typedef enum {
    LIGHT_CUE_NONE = 0,
    LIGHT_CUE_MOVE_ACCEPTED,
    LIGHT_CUE_ILLEGAL,
    LIGHT_CUE_RESULT,
    LIGHT_CUE_WIFI,
    LIGHT_CUE_COUNTDOWN,
} light_cue_t;

void hw_output_display_text(piece_color_t side, const char *text);
void hw_output_light_cue(piece_color_t side, light_cue_t cue);

#endif
