#ifndef CHESSBOARD_PORT_BOARD_HW_H
#define CHESSBOARD_PORT_BOARD_HW_H

#include "esp_err.h"

/* Brings up NVS so hw_storage_* can work. Separate from the boundary itself,
 * because core/ neither knows nor cares that persistence needs mounting.
 *
 * The hw_* boundary implementations in board_hw.c keep module-static scan and
 * text buffers, so they must be called from the application task only, like
 * every driver under port/. */
esp_err_t board_hw_storage_init(void);

#endif
