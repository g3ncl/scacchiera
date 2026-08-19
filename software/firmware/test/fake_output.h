#ifndef CHESSBOARD_TEST_FAKE_OUTPUT_H
#define CHESSBOARD_TEST_FAKE_OUTPUT_H

#include "core/hw/output.h"

#define FAKE_OUTPUT_TEXT_MAX 64

void fake_output_reset(void);
const char *fake_output_last_text(piece_color_t side);
light_cue_t fake_output_last_cue(piece_color_t side);

#endif
