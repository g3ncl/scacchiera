#ifndef CHESSBOARD_CORE_HW_SCAN_H
#define CHESSBOARD_CORE_HW_SCAN_H

#include <stdbool.h>

#include "core/snapshot.h"

/* One complete typed read of all 64 squares. Returns false when the scan could
 * not be completed at all; a scan that completed but found trouble returns
 * true with a fault set in the snapshot, because those are different things to
 * the layer above. */
bool hw_scan_board(board_snapshot_t *snapshot);

#endif
