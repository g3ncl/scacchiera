#ifndef CHESSBOARD_CORE_HW_BUTTON_H
#define CHESSBOARD_CORE_HW_BUTTON_H

#include <stdbool.h>

/* The single button, already debounced by being sampled once per sweep. True
 * while held. Implemented by port/ through the expander's BUTTON_N input and
 * by a deterministic fake on the host. */
bool hw_button_pressed(void);

#endif
