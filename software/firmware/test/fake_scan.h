#ifndef CHESSBOARD_TEST_FAKE_SCAN_H
#define CHESSBOARD_TEST_FAKE_SCAN_H

#include <stdbool.h>

#include "core/snapshot.h"

void fake_scan_reset(void);
/* The snapshot the next hw_scan_board call returns. */
void fake_scan_set_result(const board_snapshot_t *snapshot);
/* Make the next n scans fail outright, as distinct from returning a fault. */
void fake_scan_fail_next(unsigned count);
unsigned fake_scan_call_count(void);

#endif
