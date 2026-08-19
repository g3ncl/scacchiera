#include "core/identity.h"

bool identity_resolve(const piece_registry_t *registry, board_snapshot_t *snapshot)
{
    if (snapshot->fault.fault != BOARD_FAULT_NONE) {
        return false;
    }

    /* Two squares carrying one UID is a cloned or duplicated tag, and it is a
     * different failure from one tag being heard on two lines: the join can
     * only see the second, and only this pass can see the first. */
    square_t first = SQUARE_INVALID;
    square_t second = SQUARE_INVALID;
    if (board_snapshot_find_duplicate_uid(snapshot, &first, &second)) {
        snapshot->fault.fault = BOARD_FAULT_UID_DUPLICATE;
        snapshot->fault.square = first;
        return false;
    }

    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        square_reading_t *reading = &snapshot->squares[square];
        if (reading->state != SQUARE_STATE_OCCUPIED) {
            continue;
        }

        piece_color_t color = PIECE_COLOR_WHITE;
        piece_type_t type = PIECE_TYPE_NONE;
        if (!registry_lookup(registry, reading->uid, &color, &type)) {
            /* An unprovisioned or foreign tag. Named at its square, because
             * "remove or re-provision the indicated piece" is the recovery the
             * fault table promises and it needs a square to indicate. */
            snapshot->fault.fault = BOARD_FAULT_TAG_FAULT;
            snapshot->fault.square = square;
            return false;
        }
        reading->color = color;
        reading->type = type;
    }
    return true;
}
