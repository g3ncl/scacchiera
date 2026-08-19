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
 * instruction.
 *
 * Single-task driver: instruction sequencing around BUSY is unguarded beyond
 * the SPI bus lock, so every call here must come from the application task. */

/* 1-byte direct commands, datasheet Table 5. Only the ones this driver issues
 * are named; the rest are deliberately absent rather than listed unused. */
#define PN5180_CMD_WRITE_REGISTER 0x00u
#define PN5180_CMD_WRITE_REGISTER_OR_MASK 0x01u
#define PN5180_CMD_WRITE_REGISTER_AND_MASK 0x02u
#define PN5180_CMD_READ_REGISTER 0x04u
#define PN5180_CMD_READ_EEPROM 0x07u
#define PN5180_CMD_SEND_DATA 0x09u
#define PN5180_CMD_READ_DATA 0x0Au
#define PN5180_CMD_LOAD_RF_CONFIG 0x11u
#define PN5180_CMD_RF_ON 0x16u
#define PN5180_CMD_RF_OFF 0x17u

/* Register addresses, datasheet Table 74. */
#define PN5180_REG_SYSTEM_CONFIG 0x00u
#define PN5180_REG_IRQ_STATUS 0x02u
#define PN5180_REG_IRQ_CLEAR 0x03u
#define PN5180_REG_RX_STATUS 0x13u

/* SYSTEM_CONFIG bits 2:0 select the transceiver command; 0x3 is TRANSCEIVE,
 * which SEND_DATA requires as a precondition (datasheet Table 15). */
#define PN5180_SYSTEM_CONFIG_COMMAND_MASK 0x00000007u
#define PN5180_SYSTEM_CONFIG_COMMAND_TRANSCEIVE 0x00000003u

/* TX_CONFIG bit 10, datasheet Table 98: "If set to 1; transmission of data is
 * enabled otherwise only symbols are transmitted." Clearing it turns a
 * transmission into frame symbols alone, which is the EOF that advances an
 * ISO 15693 anticollision slot. */
#define PN5180_REG_TX_CONFIG 0x18u
#define PN5180_TX_CONFIG_DATA_ENABLE 0x00000400u

/* IRQ_STATUS bit 0. RX_STATUS bits 8:0 hold the received byte count. */
#define PN5180_IRQ_RX 0x00000001u
#define PN5180_RX_STATUS_BYTES_MASK 0x000001FFu

/* RF configuration indices, datasheet Table 40. ISO 15693 ASK100 at 26 kbit/s
 * transmitting, ISO 15693 at 26 kbit/s receiving: the pairing the SLIX2 tags
 * answer at. */
#define PN5180_RF_TX_ISO15693_ASK100_26 0x0Du
#define PN5180_RF_RX_ISO15693_26 0x8Du

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

esp_err_t pn5180_load_rf_config(uint8_t tx_config, uint8_t rx_config);
esp_err_t pn5180_send_data(const uint8_t *data, uint8_t length, uint8_t valid_bits);
esp_err_t pn5180_read_data(uint8_t *buffer, uint16_t length);
esp_err_t pn5180_received_byte_count(uint16_t *count);

/* Sixteen-slot ISO 15693 anticollision on the selected antenna, resolving a
 * collided slot by re-running the round with the mask extended by that slot's
 * four bits (ISO/IEC 15693-3). The recursion is what makes a fully occupied
 * line readable at all: eight tags in sixteen slots collide far more often
 * than not, and the slot a tag picks is UID-derived, so no retry helps.
 *
 * Fills up to capacity UIDs and reports how many answered. Sets incomplete
 * when a collision survived the mask and round budgets or more tags answered
 * than fit, which means the line is known to be under-reported rather than
 * empty. BitwiseID, which reads a whole line in one operation instead of slot
 * by slot, remains the later throughput increment. */
esp_err_t pn5180_iso15693_inventory_16(uint64_t *uids, uint8_t capacity,
                                       uint8_t *found, bool *incomplete);

pn5180_version_t pn5180_product_version(void);
pn5180_version_t pn5180_firmware_version(void);

#endif
