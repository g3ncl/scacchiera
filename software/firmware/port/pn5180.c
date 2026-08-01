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

/* The datasheet describes a LOW on RESET_N as a power-down but gives no
 * minimum pulse width, so this is chosen rather than sourced: long enough that
 * the internal regulators are unambiguously down, short enough to be free at
 * boot. Not a datasheet figure and marked as such. */
#define RESET_LOW_MS 10
#define RESET_SETTLE_MS 10

static spi_device_handle_t s_device;
static pn5180_version_t s_product;
static pn5180_version_t s_firmware;

static esp_err_t wait_busy(bool level)
{
    const int64_t deadline = esp_timer_get_time() + BUSY_TIMEOUT_US;
    while (gpio_get_level(PIN_NFC_BUSY) != (level ? 1 : 0)) {
        if (esp_timer_get_time() > deadline) {
            ESP_LOGE(TAG, "BUSY stuck %s", level ? "low" : "high");
            return ESP_ERR_TIMEOUT;
        }
        esp_rom_delay_us(5);
    }
    return ESP_OK;
}

/* One instruction: NSS low for the whole frame, then BUSY back to idle.
 *
 * Step 3 of the datasheet's recommended sequence, waiting for BUSY high before
 * deasserting NSS, is optional while the test bus is disabled, and ESP-IDF
 * owns NSS so it cannot be honoured without bit-banging chip select. Waiting
 * for BUSY to fall afterwards is the part that matters, because it is what
 * makes the next instruction safe to start. */
static esp_err_t send_instruction(const uint8_t *frame, size_t length)
{
    ESP_RETURN_ON_ERROR(wait_busy(false), TAG, "busy before send");
    spi_transaction_t transaction = {
        .length = length * 8u,
        .tx_buffer = frame,
    };
    ESP_RETURN_ON_ERROR(spi_device_polling_transmit(s_device, &transaction), TAG, "send");
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
    /* Command, the valid-bit count for the last byte, then the payload. */
    uint8_t frame[3 + 8];
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

/* ISO/IEC 15693 inventory, single slot.
 *
 * Flags 0x26 is inventory (bit 2) plus high data rate (bit 1) plus one slot
 * (bit 5). One slot means every tag in the field answers in the same window,
 * so two tags collide and the response comes back malformed rather than as
 * two UIDs. That is reported as INVALID_RESPONSE and is exactly the
 * RF_CROSSTALK condition the fault table describes. */
#define ISO15693_FLAGS_INVENTORY_ONE_SLOT 0x26u
#define ISO15693_CMD_INVENTORY 0x01u
#define ISO15693_INVENTORY_RESPONSE_BYTES 10u

esp_err_t pn5180_iso15693_inventory(uint64_t *uid)
{
    if (uid == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    /* Clearing every IRQ first: a stale RX flag from the previous line would
     * be read as this line's answer. */
    ESP_RETURN_ON_ERROR(pn5180_write_register(PN5180_REG_IRQ_CLEAR, 0xFFFFFFFFu),
                        TAG, "irq clear");

    /* SEND_DATA requires SYSTEM_CONFIG.COMMAND set to TRANSCEIVE beforehand
     * (datasheet Table 15), left as a read-modify-write so the rest of the
     * register survives. */
    uint32_t system_config = 0;
    ESP_RETURN_ON_ERROR(pn5180_read_register(PN5180_REG_SYSTEM_CONFIG, &system_config),
                        TAG, "system config");
    system_config &= ~PN5180_SYSTEM_CONFIG_COMMAND_MASK;
    system_config |= PN5180_SYSTEM_CONFIG_COMMAND_TRANSCEIVE;
    ESP_RETURN_ON_ERROR(pn5180_write_register(PN5180_REG_SYSTEM_CONFIG, system_config),
                        TAG, "transceive");

    const uint8_t inventory[3] = {
        ISO15693_FLAGS_INVENTORY_ONE_SLOT,
        ISO15693_CMD_INVENTORY,
        0x00u, /* mask length zero: no addressing, everyone answers */
    };
    ESP_RETURN_ON_ERROR(pn5180_send_data(inventory, sizeof(inventory), 0), TAG, "inventory");

    /* An empty square is the normal case, so a silent field is not an error
     * path worth logging. The wait covers one slot at 26 kbit/s with margin. */
    const int64_t deadline = esp_timer_get_time() + 20000;
    uint32_t irq = 0;
    do {
        ESP_RETURN_ON_ERROR(pn5180_read_register(PN5180_REG_IRQ_STATUS, &irq), TAG, "irq");
        if ((irq & PN5180_IRQ_RX) != 0u) {
            break;
        }
    } while (esp_timer_get_time() < deadline);

    if ((irq & PN5180_IRQ_RX) == 0u) {
        return ESP_ERR_NOT_FOUND;
    }

    uint16_t received = 0;
    ESP_RETURN_ON_ERROR(pn5180_received_byte_count(&received), TAG, "count");
    if (received != ISO15693_INVENTORY_RESPONSE_BYTES) {
        /* Flags, DSFID and eight UID bytes is the only well-formed answer.
         * Anything else is a collision or a corrupted frame, and neither may
         * become a piece. */
        return ESP_ERR_INVALID_RESPONSE;
    }

    uint8_t response[ISO15693_INVENTORY_RESPONSE_BYTES] = {0};
    ESP_RETURN_ON_ERROR(pn5180_read_data(response, sizeof(response)), TAG, "read data");

    /* response[0] flags, response[1] DSFID, response[2..9] UID least
     * significant byte first. */
    uint64_t value = 0;
    for (int index = 7; index >= 0; index--) {
        value = (value << 8) | response[2 + index];
    }
    *uid = value;
    return ESP_OK;
}
