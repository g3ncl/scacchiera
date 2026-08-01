#ifndef CHESSBOARD_TEST_FAKE_CLOCK_H
#define CHESSBOARD_TEST_FAKE_CLOCK_H

#include <stdint.h>

void fake_clock_reset(void);
void fake_clock_set(uint32_t ms);
void fake_clock_advance(uint32_t ms);

#endif
