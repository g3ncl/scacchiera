#include "core/fault.h"

#include <stddef.h>

static const char *const FAULT_NAMES[BOARD_FAULT_COUNT] = {
    [BOARD_FAULT_NONE] = "NONE",
    [BOARD_FAULT_TAG_FAULT] = "TAG_FAULT",
    [BOARD_FAULT_UID_DUPLICATE] = "UID_DUPLICATE",
    [BOARD_FAULT_RF_CROSSTALK] = "RF_CROSSTALK",
    [BOARD_FAULT_SQUARE_UNSTABLE] = "SQUARE_UNSTABLE",
    [BOARD_FAULT_BOARD_MISMATCH] = "BOARD_MISMATCH",
};

const char *board_fault_name(board_fault_t fault)
{
    if (fault >= BOARD_FAULT_COUNT) {
        return "UNKNOWN";
    }
    const char *name = FAULT_NAMES[fault];
    return (name != NULL) ? name : "UNKNOWN";
}
