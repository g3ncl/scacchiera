#ifndef CHESSBOARD_PORT_BOARD_HW_H
#define CHESSBOARD_PORT_BOARD_HW_H

#include "esp_err.h"

/* Brings up NVS so hw_storage_* can work. Separate from the boundary itself,
 * because core/ neither knows nor cares that persistence needs mounting. */
esp_err_t board_hw_storage_init(void);

#endif
