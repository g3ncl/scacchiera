#include "fake_storage.h"

#include <string.h>

#include "core/hw/storage.h"

static board_snapshot_t g_stored;
static bool g_has_snapshot;
static bool g_corrupt;
static unsigned g_failures_remaining;
static unsigned g_writes;

void fake_storage_reset(void)
{
    board_snapshot_clear(&g_stored);
    g_has_snapshot = false;
    g_corrupt = false;
    g_failures_remaining = 0u;
    g_writes = 0u;
}

void fake_storage_fail_writes(unsigned count)
{
    g_failures_remaining = count;
}

void fake_storage_corrupt(void)
{
    g_corrupt = true;
}

bool fake_storage_has_snapshot(void)
{
    return g_has_snapshot && !g_corrupt;
}

unsigned fake_storage_write_count(void)
{
    return g_writes;
}

bool hw_storage_save_snapshot(const board_snapshot_t *snapshot)
{
    g_writes++;
    if (g_failures_remaining > 0u) {
        g_failures_remaining--;
        /* A failed write must not leave a half-written snapshot readable. */
        g_corrupt = true;
        return false;
    }
    g_stored = *snapshot;
    g_has_snapshot = true;
    g_corrupt = false;
    return true;
}

bool hw_storage_load_snapshot(board_snapshot_t *snapshot)
{
    if (!g_has_snapshot || g_corrupt) {
        return false;
    }
    *snapshot = g_stored;
    return true;
}

bool hw_storage_clear(void)
{
    board_snapshot_clear(&g_stored);
    g_has_snapshot = false;
    g_corrupt = false;
    return true;
}
