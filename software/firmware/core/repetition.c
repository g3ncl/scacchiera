#include "core/repetition.h"

void repetition_reset(repetition_t *ledger, uint64_t key)
{
    ledger->count = 0u;
    repetition_push(ledger, key);
}

void repetition_push(repetition_t *ledger, uint64_t key)
{
    if (ledger->count < REPETITION_MAX_PLIES) {
        ledger->keys[ledger->count++] = key;
        return;
    }
    /* Reaching the end means the 75-move rule has already ended the game, so
     * dropping the oldest entry cannot lose a claim anyone could still make.
     * Overwriting rather than refusing keeps the newest window intact. */
    for (uint8_t index = 1u; index < REPETITION_MAX_PLIES; index++) {
        ledger->keys[index - 1u] = ledger->keys[index];
    }
    ledger->keys[REPETITION_MAX_PLIES - 1u] = key;
}

uint8_t repetition_count(const repetition_t *ledger, uint64_t key)
{
    uint8_t occurrences = 0u;
    for (uint8_t index = 0u; index < ledger->count; index++) {
        if (ledger->keys[index] == key) {
            occurrences++;
        }
    }
    return occurrences;
}
