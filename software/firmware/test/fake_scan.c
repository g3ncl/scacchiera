#include "fake_scan.h"

#include <string.h>

#include "core/hw/scan.h"

static board_snapshot_t g_result;
static unsigned g_failures_remaining;
static unsigned g_calls;

void fake_scan_reset(void)
{
    board_snapshot_clear(&g_result);
    g_failures_remaining = 0u;
    g_calls = 0u;
}

void fake_scan_set_result(const board_snapshot_t *snapshot)
{
    g_result = *snapshot;
}

void fake_scan_fail_next(unsigned count)
{
    g_failures_remaining = count;
}

unsigned fake_scan_call_count(void)
{
    return g_calls;
}

bool hw_scan_board(board_snapshot_t *snapshot)
{
    g_calls++;
    if (g_failures_remaining > 0u) {
        g_failures_remaining--;
        return false;
    }
    *snapshot = g_result;
    return true;
}
