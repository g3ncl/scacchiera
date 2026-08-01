#include "fake_output.h"

#include <string.h>

static char g_text[2][FAKE_OUTPUT_TEXT_MAX];
static light_cue_t g_cue[2];

void fake_output_reset(void)
{
    memset(g_text, 0, sizeof(g_text));
    g_cue[0] = LIGHT_CUE_NONE;
    g_cue[1] = LIGHT_CUE_NONE;
}

const char *fake_output_last_text(piece_color_t side)
{
    return g_text[side];
}

light_cue_t fake_output_last_cue(piece_color_t side)
{
    return g_cue[side];
}

void hw_output_display_text(piece_color_t side, const char *text)
{
    strncpy(g_text[side], text, FAKE_OUTPUT_TEXT_MAX - 1u);
    g_text[side][FAKE_OUTPUT_TEXT_MAX - 1u] = '\0';
}

void hw_output_light_cue(piece_color_t side, light_cue_t cue)
{
    g_cue[side] = cue;
}
