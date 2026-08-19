#include "port/pn5180.h"

#include <string.h>

#include "driver/gpio.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_rom_sys.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "port/board_pins.h"
#include "port/expander.h"
#include "port/spi_bus.h"

static const char *TAG = "pn5180";

/* 5 MHz against the datasheet's 7 Mbit/s ceiling. The margin is for the
 * unterminated link to the reader, not for the part. */
#define PN5180_CLOCK_HZ 5000000

/* BUSY should clear in microseconds. A millisecond ceiling turns a wiring
 * fault or a dead reader into a prompt error instead of a hang. */
#define BUSY_TIMEOUT_US 100000

/* How long the BUSY rise is watched for after a frame. Datasheet section
 * 11.4.1: BUSY goes active during frame reception, so it is normally already
 * high when polling starts; a fast instruction can also complete inside one
 * poll interval, so a missed rise is tolerated rather than an error. The
 * window only has to outlast a part that is slow to start. Chosen rather
 * than sourced: the datasheet gives no rise-latency figure. */
#define BUSY_RISE_TIMEOUT_US 1000

/* The datasheet describes a LOW on RESET_N as a power-down but gives no
 * minimum pulse width, so this is chosen rather than sourced: long enough that
 * the internal regulators are unambiguously down, short enough to be free at
 * boot. Not a datasheet figure and marked as such. */
#define RESET_LOW_MS 10
#define RESET_SETTLE_MS 10

static spi_device_handle_t s_device;
static pn5180_version_t s_product;
static pn5180_version_t s_firmware;

static esp_err_t wait_busy_for(bool level, int64_t timeout_us, bool loud)
{
    const int64_t deadline = esp_timer_get_time() + timeout_us;
    while (gpio_get_level(PIN_NFC_BUSY) != (level ? 1 : 0)) {
        if (esp_timer_get_time() > deadline) {
            if (loud) {
                ESP_LOGE(TAG, "BUSY stuck %s", level ? "low" : "high");
            }
            return ESP_ERR_TIMEOUT;
        }
        esp_rom_delay_us(5);
    }
    return ESP_OK;
}

static esp_err_t wait_busy(bool level)
{
    return wait_busy_for(level, BUSY_TIMEOUT_US, true);
}

/* One instruction: NSS low for the whole frame, then BUSY observed around the
 * processing.
 *
 * Datasheet section 11.4.1: BUSY goes active during frame reception and
 * returns to idle when the part can take a new frame or has data ready, and
 * the recommended sequence is exchange, wait BUSY high (optional in normal
 * mode), deassert NSS, wait BUSY low. ESP-IDF owns NSS, so the deassert lands
 * right after the transfer; the rise is then watched briefly before the fall
 * is waited on, because a fall never preceded by an observed rise cannot
 * distinguish "finished" from "not started yet". A missed rise means the
 * instruction already completed, which the tolerated timeout covers. */
static esp_err_t send_instruction(const uint8_t *frame, size_t length)
{
    ESP_RETURN_ON_ERROR(wait_busy(false), TAG, "busy before send");
    spi_transaction_t transaction = {
        .length = length * 8u,
        .tx_buffer = frame,
    };
    ESP_RETURN_ON_ERROR(spi_device_polling_transmit(s_device, &transaction), TAG, "send");
    (void)wait_busy_for(true, BUSY_RISE_TIMEOUT_US, false);
    return wait_busy(false);
}

static esp_err_t read_response(uint8_t *buffer, size_t length)
{
    ESP_RETURN_ON_ERROR(wait_busy(false), TAG, "busy before read");
    spi_transaction_t transaction = {
        .length = length * 8u,
        .rxlength = length * 8u,
        .rx_buffer = buffer,
    };
    ESP_RETURN_ON_ERROR(spi_device_polling_transmit(s_device, &transaction), TAG, "read");
    (void)wait_busy_for(true, BUSY_RISE_TIMEOUT_US, false);
    return wait_busy(false);
}

/* A read is two instructions with the bus held across both. Releasing it
 * between them would let a display transfer land where the response belongs,
 * and would also clock that traffic into the matrix registers. */
static esp_err_t instruction_with_response(const uint8_t *frame, size_t frame_length,
                                           uint8_t *buffer, size_t buffer_length)
{
    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device, portMAX_DELAY), TAG, "acquire");
    esp_err_t err = send_instruction(frame, frame_length);
    if (err == ESP_OK) {
        err = read_response(buffer, buffer_length);
    }
    spi_device_release_bus(s_device);
    return err;
}

esp_err_t pn5180_read_register(uint8_t address, uint32_t *value)
{
    if (value == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    const uint8_t frame[2] = {PN5180_CMD_READ_REGISTER, address};
    uint8_t response[4] = {0};
    ESP_RETURN_ON_ERROR(instruction_with_response(frame, sizeof(frame), response, sizeof(response)),
                        TAG, "read register");
    /* Registers come back least significant byte first. */
    *value = (uint32_t)response[0] | ((uint32_t)response[1] << 8) |
             ((uint32_t)response[2] << 16) | ((uint32_t)response[3] << 24);
    return ESP_OK;
}

esp_err_t pn5180_write_register(uint8_t address, uint32_t value)
{
    const uint8_t frame[6] = {
        PN5180_CMD_WRITE_REGISTER,
        address,
        (uint8_t)(value & 0xFFu),
        (uint8_t)((value >> 8) & 0xFFu),
        (uint8_t)((value >> 16) & 0xFFu),
        (uint8_t)((value >> 24) & 0xFFu),
    };
    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device, portMAX_DELAY), TAG, "acquire");
    const esp_err_t err = send_instruction(frame, sizeof(frame));
    spi_device_release_bus(s_device);
    return err;
}

esp_err_t pn5180_read_eeprom(uint8_t address, uint8_t *buffer, uint8_t length)
{
    if (buffer == NULL || length == 0u) {
        return ESP_ERR_INVALID_ARG;
    }
    const uint8_t frame[3] = {PN5180_CMD_READ_EEPROM, address, length};
    return instruction_with_response(frame, sizeof(frame), buffer, length);
}

esp_err_t pn5180_rf_field(bool on)
{
    /* Both take one parameter byte, which is reserved and sent as zero. */
    const uint8_t frame[2] = {on ? PN5180_CMD_RF_ON : PN5180_CMD_RF_OFF, 0x00u};
    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device, portMAX_DELAY), TAG, "acquire");
    const esp_err_t err = send_instruction(frame, sizeof(frame));
    spi_device_release_bus(s_device);
    return err;
}

esp_err_t pn5180_reset(void)
{
    ESP_RETURN_ON_ERROR(expander_set(EXP_NFC_RESET_N_PORT, EXP_NFC_RESET_N_BIT, false),
                        TAG, "reset assert");
    vTaskDelay(pdMS_TO_TICKS(RESET_LOW_MS));
    ESP_RETURN_ON_ERROR(expander_set(EXP_NFC_RESET_N_PORT, EXP_NFC_RESET_N_BIT, true),
                        TAG, "reset release");
    vTaskDelay(pdMS_TO_TICKS(RESET_SETTLE_MS));
    return wait_busy(false);
}

esp_err_t pn5180_init(void)
{
    const gpio_config_t busy_config = {
        .pin_bit_mask = 1ULL << PIN_NFC_BUSY,
        .mode = GPIO_MODE_INPUT,
        /* The PN5180 drives BUSY and enables its own internal pull-down on
         * power-down, so no pull is added here. */
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_RETURN_ON_ERROR(gpio_config(&busy_config), TAG, "busy gpio");

    const spi_device_interface_config_t config = {
        .mode = 0,
        .clock_speed_hz = PN5180_CLOCK_HZ,
        .spics_io_num = PIN_NFC_CS_N,
        .queue_size = 1,
    };
    ESP_RETURN_ON_ERROR(spi_bus_add_device(CHESSBOARD_SPI_HOST, &config, &s_device),
                        TAG, "add device");

    ESP_RETURN_ON_ERROR(pn5180_reset(), TAG, "reset");

    /* Liveness. Two EEPROM reads exercise a command frame, both BUSY edges and
     * a response frame, so a miswired BUSY or a transposed MISO fails here
     * with a clear message rather than later as an empty board. */
    uint8_t product[2] = {0};
    ESP_RETURN_ON_ERROR(pn5180_read_eeprom(PN5180_EEPROM_PRODUCT_VERSION, product, sizeof(product)),
                        TAG, "product version");
    uint8_t firmware[2] = {0};
    ESP_RETURN_ON_ERROR(pn5180_read_eeprom(PN5180_EEPROM_FIRMWARE_VERSION, firmware, sizeof(firmware)),
                        TAG, "firmware version");

    /* Minor byte first, then major: datasheet Table 51 gives FW 4.1 as 0x12
     * holding 0x01 and 0x13 holding 0x04. */
    s_product = (pn5180_version_t){.minor = product[0], .major = product[1]};
    s_firmware = (pn5180_version_t){.minor = firmware[0], .major = firmware[1]};

    if (s_product.major == 0xFFu || s_product.major == 0x00u) {
        /* An all-ones or all-zeroes read is what an absent or unclocked
         * device looks like, not a real version. */
        ESP_LOGE(TAG, "implausible product version %u.%u, check SPI and BUSY",
                 s_product.major, s_product.minor);
        return ESP_ERR_INVALID_RESPONSE;
    }

    ESP_LOGI(TAG, "product %u.%u, firmware %u.%u",
             s_product.major, s_product.minor, s_firmware.major, s_firmware.minor);
    return ESP_OK;
}

pn5180_version_t pn5180_product_version(void)
{
    return s_product;
}

pn5180_version_t pn5180_firmware_version(void)
{
    return s_firmware;
}

esp_err_t pn5180_load_rf_config(uint8_t tx_config, uint8_t rx_config)
{
    const uint8_t frame[3] = {PN5180_CMD_LOAD_RF_CONFIG, tx_config, rx_config};
    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device, portMAX_DELAY), TAG, "acquire");
    const esp_err_t err = send_instruction(frame, sizeof(frame));
    spi_device_release_bus(s_device);
    return err;
}

esp_err_t pn5180_send_data(const uint8_t *data, uint8_t length, uint8_t valid_bits)
{
    if (data == NULL || length == 0u) {
        return ESP_ERR_INVALID_ARG;
    }
    /* Command, the valid-bit count for the last byte, then the payload.
     * Sized for the largest frame this driver sends: an anticollision
     * inventory carrying a full 60-bit mask is 11 payload bytes. */
    uint8_t frame[2 + 16];
    if ((size_t)length + 2u > sizeof(frame)) {
        return ESP_ERR_INVALID_SIZE;
    }
    frame[0] = PN5180_CMD_SEND_DATA;
    frame[1] = valid_bits;
    memcpy(&frame[2], data, length);

    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device, portMAX_DELAY), TAG, "acquire");
    const esp_err_t err = send_instruction(frame, (size_t)length + 2u);
    spi_device_release_bus(s_device);
    return err;
}

esp_err_t pn5180_read_data(uint8_t *buffer, uint16_t length)
{
    if (buffer == NULL || length == 0u) {
        return ESP_ERR_INVALID_ARG;
    }
    const uint8_t frame[2] = {PN5180_CMD_READ_DATA, 0x00u};
    return instruction_with_response(frame, sizeof(frame), buffer, length);
}

esp_err_t pn5180_received_byte_count(uint16_t *count)
{
    if (count == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    uint32_t status = 0;
    ESP_RETURN_ON_ERROR(pn5180_read_register(PN5180_REG_RX_STATUS, &status), TAG, "rx status");
    *count = (uint16_t)(status & PN5180_RX_STATUS_BYTES_MASK);
    return ESP_OK;
}

/* ISO/IEC 15693 inventory framing.
 *
 * Flags 0x06 is inventory (bit 2) plus high data rate (bit 1) with the
 * one-slot bit clear, so a round runs all sixteen slots. The only well-formed
 * answer is flags, DSFID and eight UID bytes; anything else in a slot is a
 * collision or a corrupted frame, and neither may become a piece. */
#define ISO15693_FLAGS_INVENTORY_16 0x06u
#define ISO15693_CMD_INVENTORY 0x01u
#define ISO15693_INVENTORY_RESPONSE_BYTES 10u

/* A mask can name at most 60 bits of the 64-bit UID (ISO/IEC 15693-3), which
 * is what bounds the anticollision splitting. */
#define ISO15693_MASK_BITS_MAX 60u

/* Rounds one full anticollision pass may spend before the line is declared
 * under-read. Eight tags splitting only at the last mask level need 1 + 15
 * rounds; a real line resolves in one or two, so the budget is a backstop
 * against pathological or coupled populations, not a working figure. */
#define INVENTORY_MAX_ROUNDS 16u

/* How long a slot is given before it counts as empty.
 *
 * This is the dominant term in scan time and therefore in scan energy, because
 * most slots in a real position are empty and each one costs the whole timeout.
 * A starting position leaves eight of sixteen slots silent on a populated line
 * and all sixteen on an empty one, so the board pays this timeout far more
 * often than it pays for an answer.
 *
 * The bound is the longest legitimate answer, not a round number. An inventory
 * response is flags, a 64-bit UID and a CRC, so 88 bits at the 26 kbit/s high
 * data rate is about 3.4 ms, after a start delay of roughly 0.3 ms. Six
 * milliseconds covers that with about sixty percent in hand.
 *
 * A tighter bound is available and deliberately not taken: the reader can
 * report that a subcarrier was detected (IRQ_STATUS bit 15, RX_SC_DET), which
 * decides an empty slot in about a third of a millisecond rather than six.
 * Wiring that in is a measured-throughput change for the bench, not a guess
 * to make here. */
#define SLOT_TIMEOUT_US 6000

static esp_err_t set_transceive(void)
{
    uint32_t system_config = 0;
    ESP_RETURN_ON_ERROR(pn5180_read_register(PN5180_REG_SYSTEM_CONFIG, &system_config),
                        TAG, "system config");
    system_config &= ~PN5180_SYSTEM_CONFIG_COMMAND_MASK;
    system_config |= PN5180_SYSTEM_CONFIG_COMMAND_TRANSCEIVE;
    return pn5180_write_register(PN5180_REG_SYSTEM_CONFIG, system_config);
}

static esp_err_t set_tx_data_enable(bool enable)
{
    uint32_t tx_config = 0;
    ESP_RETURN_ON_ERROR(pn5180_read_register(PN5180_REG_TX_CONFIG, &tx_config),
                        TAG, "tx config");
    if (enable) {
        tx_config |= PN5180_TX_CONFIG_DATA_ENABLE;
    } else {
        tx_config &= ~PN5180_TX_CONFIG_DATA_ENABLE;
    }
    return pn5180_write_register(PN5180_REG_TX_CONFIG, tx_config);
}

/* Waits one slot. Returns ESP_OK with the byte count when something answered,
 * ESP_ERR_NOT_FOUND on an empty slot. */
static esp_err_t await_slot(uint16_t *received)
{
    const int64_t deadline = esp_timer_get_time() + SLOT_TIMEOUT_US;
    uint32_t irq = 0;
    do {
        ESP_RETURN_ON_ERROR(pn5180_read_register(PN5180_REG_IRQ_STATUS, &irq), TAG, "irq");
        if ((irq & PN5180_IRQ_RX) != 0u) {
            return pn5180_received_byte_count(received);
        }
    } while (esp_timer_get_time() < deadline);
    return ESP_ERR_NOT_FOUND;
}

/* Emits an EOF with no payload, advancing the inventory to the next slot.
 *
 * SEND_DATA will not accept a zero-length array, so one dummy byte is passed
 * with TX_DATA_ENABLE cleared: the datasheet says only symbols are transmitted
 * in that state, so the byte never reaches the air. */
static esp_err_t next_slot(void)
{
    ESP_RETURN_ON_ERROR(pn5180_write_register(PN5180_REG_IRQ_CLEAR, 0xFFFFFFFFu),
                        TAG, "irq clear");
    ESP_RETURN_ON_ERROR(set_tx_data_enable(false), TAG, "data off");
    ESP_RETURN_ON_ERROR(set_transceive(), TAG, "transceive");
    const uint8_t dummy = 0x00u;
    return pn5180_send_data(&dummy, 1, 0);
}

/* One sixteen-slot round with `mask_bits` of `mask` pre-selecting the
 * responders: only tags whose UID starts with the mask answer, and the slot a
 * tag picks is its next four UID bits. Collided slots are reported to the
 * caller, which decides whether to run a deeper round. */
static esp_err_t inventory_round(uint64_t mask, uint8_t mask_bits, uint64_t *uids,
                                 uint8_t capacity, uint8_t *found, bool *incomplete,
                                 uint8_t collided[16], uint8_t *collided_count)
{
    *collided_count = 0u;

    /* Clearing every IRQ first: a stale RX flag from the previous line or
     * round would be read as this round's answer. */
    ESP_RETURN_ON_ERROR(pn5180_write_register(PN5180_REG_IRQ_CLEAR, 0xFFFFFFFFu),
                        TAG, "irq clear");
    ESP_RETURN_ON_ERROR(set_tx_data_enable(true), TAG, "data on");
    ESP_RETURN_ON_ERROR(set_transceive(), TAG, "transceive");

    /* Flags, command, mask length in bits, then the mask value padded with
     * zeros to whole bytes (ISO/IEC 15693-3), least significant byte first
     * like every other 15693 field. */
    uint8_t frame[3 + 8];
    frame[0] = ISO15693_FLAGS_INVENTORY_16;
    frame[1] = ISO15693_CMD_INVENTORY;
    frame[2] = mask_bits;
    const uint8_t mask_bytes = (uint8_t)((mask_bits + 7u) / 8u);
    for (uint8_t index = 0u; index < mask_bytes; index++) {
        frame[3u + index] = (uint8_t)(mask >> (8u * index));
    }
    ESP_RETURN_ON_ERROR(pn5180_send_data(frame, (uint8_t)(3u + mask_bytes), 0),
                        TAG, "inventory");

    for (uint8_t slot = 0u; slot < 16u; slot++) {
        if (slot > 0u) {
            ESP_RETURN_ON_ERROR(next_slot(), TAG, "next slot");
        }

        uint16_t received = 0u;
        const esp_err_t err = await_slot(&received);
        if (err == ESP_ERR_NOT_FOUND) {
            continue; /* empty slot, the common case */
        }
        ESP_RETURN_ON_ERROR(err, TAG, "slot");

        if (received != ISO15693_INVENTORY_RESPONSE_BYTES) {
            /* Two tags answered in this slot. The caller resolves it with a
             * longer mask rather than reporting it, because the slot a tag
             * picks is UID-derived and a plain retry reshuffles nothing. */
            collided[(*collided_count)++] = slot;
            continue;
        }

        uint8_t response[ISO15693_INVENTORY_RESPONSE_BYTES] = {0};
        ESP_RETURN_ON_ERROR(pn5180_read_data(response, sizeof(response)), TAG, "read data");

        if (*found >= capacity) {
            /* More tags than a line can legitimately hold, so something is
             * coupling from a neighbour. */
            *incomplete = true;
            continue;
        }
        /* response[0] flags, response[1] DSFID, response[2..9] UID least
         * significant byte first. */
        uint64_t uid = 0;
        for (int index = 7; index >= 0; index--) {
            uid = (uid << 8) | response[2 + index];
        }
        uids[(*found)++] = uid;
    }
    return ESP_OK;
}

esp_err_t pn5180_iso15693_inventory_16(uint64_t *uids, uint8_t capacity,
                                       uint8_t *found, bool *incomplete)
{
    if (uids == NULL || found == NULL || incomplete == NULL || capacity == 0u) {
        return ESP_ERR_INVALID_ARG;
    }
    *found = 0;
    *incomplete = false;

    /* Pending masks form a work list rather than call recursion, so the
     * deepest pathological split costs table entries instead of task stack.
     * With eight tags in sixteen slots the first round collides about 88% of
     * the time on a full line, so this list is the normal path to reading a
     * starting position, not an edge case. */
    struct {
        uint64_t mask;
        uint8_t bits;
    } pending[INVENTORY_MAX_ROUNDS];
    uint8_t pending_count = 1u;
    pending[0].mask = 0u;
    pending[0].bits = 0u;

    for (uint8_t round = 0u; round < INVENTORY_MAX_ROUNDS && pending_count > 0u;
         round++) {
        pending_count--;
        const uint64_t mask = pending[pending_count].mask;
        const uint8_t bits = pending[pending_count].bits;

        uint8_t collided[16];
        uint8_t collided_count = 0u;
        ESP_RETURN_ON_ERROR(inventory_round(mask, bits, uids, capacity, found,
                                            incomplete, collided, &collided_count),
                            TAG, "round");

        for (uint8_t index = 0u; index < collided_count; index++) {
            if (bits >= ISO15693_MASK_BITS_MAX ||
                pending_count >= INVENTORY_MAX_ROUNDS) {
                /* Mask exhausted (two tags agreeing on 60 UID bits should not
                 * exist) or more splits than the budget will ever run: the
                 * line is under-read, not empty. */
                *incomplete = true;
                continue;
            }
            pending[pending_count].mask = mask | ((uint64_t)collided[index] << bits);
            pending[pending_count].bits = (uint8_t)(bits + 4u);
            pending_count++;
        }
    }
    if (pending_count > 0u) {
        /* The round budget ran out with splits still pending. */
        *incomplete = true;
    }

    /* Leave data transmission enabled, or the next ordinary command would send
     * symbols only. */
    return set_tx_data_enable(true);
}
