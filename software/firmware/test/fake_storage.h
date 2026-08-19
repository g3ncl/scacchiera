#ifndef CHESSBOARD_TEST_FAKE_STORAGE_H
#define CHESSBOARD_TEST_FAKE_STORAGE_H

#include <stdbool.h>

void fake_storage_reset(void);
/* Fail the next n writes, so a test can inject failure at each transaction
 * boundary rather than only at the first. */
void fake_storage_fail_writes(unsigned count);
/* Drop whatever is stored without clearing it cleanly, modelling a reset
 * partway through a write. */
void fake_storage_corrupt(void);
bool fake_storage_has_game(void);
unsigned fake_storage_write_count(void);

#endif
