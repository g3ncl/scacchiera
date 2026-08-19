#ifndef CHESSBOARD_CORE_HW_CLOCK_H
#define CHESSBOARD_CORE_HW_CLOCK_H

#include <stdint.h>

/* Monotonic milliseconds since boot. Implemented by port/ on the target and by
 * a deterministic fake on the host, which is what makes clock, countdown and
 * sleep behaviour testable without waiting in real time. */
uint32_t hw_clock_now_ms(void);

#endif
