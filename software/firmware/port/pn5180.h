#ifndef CHESSBOARD_PORT_PN5180_H
#define CHESSBOARD_PORT_PN5180_H

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

/* PN5180 NFC frontend on the shared SPI bus, with its own chip select on the
 * MCU and its reset line behind the expander.
 *
 * The framing is the part worth getting right, because V6 has to model it:
 * every instruction is one uninterrupted NSS assertion, and each one is
 * bracketed by BUSY. Reads are two instructions, not one duplex transfer.
 *
 * Datasheet rev 4.3, section 11.4: SPI is fixed at CPOL 0 CPHA 0, 7 Mbit/s
 * maximum, half duplex only, no chaining, and NSS must stay low for a whole
 * instruction. */

/* 1-byte direct commands, datasheet Table 5. Only the ones this driver issues
 * are named; the rest are deliberately absent rather than listed unused. */
#define PN5180_CMD_WRITE_REGISTER 0x00u
#define PN5180_CMD_READ_REGISTER 0x04u
#define PN5180_CMD_READ_EEPROM 0x07u
#define PN5180_CMD_RF_ON 0x16u
#define PN5180_CMD_RF_OFF 0x17u

/* EEPROM addresses, datasheet Table 51. */
#define PN5180_EEPROM_DIE_IDENTIFIER 0x00u
#define PN5180_EEPROM_PRODUCT_VERSION 0x10u
#define PN5180_EEPROM_FIRMWARE_VERSION 0x12u

typedef struct {
    uint8_t major;
    uint8_t minor;
} pn5180_version_t;

/* Attaches to the bus, drives a hardware reset, and reads the product and
 * firmware versions back. That read is the liveness check: it exercises a
 * command frame, both BUSY transitions and a response frame, so a wiring or
 * framing fault shows up here rather than as a silent absence of tags. */
esp_err_t pn5180_init(void);

esp_err_t pn5180_reset(void);

esp_err_t pn5180_read_register(uint8_t address, uint32_t *value);
esp_err_t pn5180_write_register(uint8_t address, uint32_t value);
esp_err_t pn5180_read_eeprom(uint8_t address, uint8_t *buffer, uint8_t length);

esp_err_t pn5180_rf_field(bool on);

pn5180_version_t pn5180_product_version(void);
pn5180_version_t pn5180_firmware_version(void);

#endif
