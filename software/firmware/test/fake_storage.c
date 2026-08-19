#include "fake_storage.h"

#include <string.h>

#include "core/hw/storage.h"

static game_record_t g_game;
static bool g_has_game;
static piece_registry_t g_registry;
static bool g_has_registry;
static unsigned g_failures_remaining;
static unsigned g_writes;

void fake_storage_reset(void)
{
    memset(&g_game, 0, sizeof(g_game));
    memset(&g_registry, 0, sizeof(g_registry));
    g_has_game = false;
    g_has_registry = false;
    g_failures_remaining = 0u;
    g_writes = 0u;
}

void fake_storage_fail_writes(unsigned count)
{
    g_failures_remaining = count;
}

void fake_storage_corrupt(void)
{
    /* Left present but unverifiable, which is what a reset partway through a
     * write leaves behind. The loader must refuse it rather than trust the
     * bytes it can see. */
    g_game.crc32 = ~g_game.crc32;
}

bool fake_storage_has_game(void)
{
    return g_has_game;
}

unsigned fake_storage_write_count(void)
{
    return g_writes;
}

/* One failure budget shared by both stores, because a flash part that cannot
 * take a write cannot take either kind. */
static bool write_allowed(void)
{
    g_writes++;
    if (g_failures_remaining > 0u) {
        g_failures_remaining--;
        return false;
    }
    return true;
}

bool hw_storage_save_game(const game_record_t *record)
{
    if (!write_allowed()) {
        /* A failed write leaves nothing loadable rather than the previous
         * game, because a half-written record that still verifies is the one
         * outcome persistence must never produce. */
        g_has_game = false;
        return false;
    }
    g_game = *record;
    g_has_game = true;
    return true;
}

bool hw_storage_load_game(game_record_t *record)
{
    if (!g_has_game || !game_record_valid(&g_game)) {
        return false;
    }
    *record = g_game;
    return true;
}

bool hw_storage_clear_game(void)
{
    g_has_game = false;
    memset(&g_game, 0, sizeof(g_game));
    return true;
}

bool hw_storage_save_registry(const piece_registry_t *registry)
{
    if (!write_allowed()) {
        return false;
    }
    g_registry = *registry;
    g_has_registry = true;
    return true;
}

bool hw_storage_load_registry(piece_registry_t *registry)
{
    if (!g_has_registry || !registry_valid(&g_registry)) {
        return false;
    }
    *registry = g_registry;
    return true;
}
