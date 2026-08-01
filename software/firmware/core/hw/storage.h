#ifndef CHESSBOARD_CORE_HW_STORAGE_H
#define CHESSBOARD_CORE_HW_STORAGE_H

#include <stdbool.h>

#include "core/snapshot.h"

/* The in-progress snapshot persisted after every committed move, compared with
 * a complete physical read after restart. V5 injects reset and write failure
 * at every transaction boundary through this interface. */

bool hw_storage_save_snapshot(const board_snapshot_t *snapshot);
bool hw_storage_load_snapshot(board_snapshot_t *snapshot);
bool hw_storage_clear(void);

#endif
