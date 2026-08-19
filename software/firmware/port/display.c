#include "port/display.h"

#include <string.h>

#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "port/board_pins.h"
#include "port/expander.h"
#include "port/spi_bus.h"

static const char *TAG = "display";

/* 4 MHz, limited by the ribbon to the module rather than by the controller. */
#define DISPLAY_CLOCK_HZ 4000000

/* SSD1362 command set, datasheet section 9. Only what is issued here. */
#define CMD_SET_COLUMN 0x15u
#define CMD_SET_ROW 0x75u
#define CMD_SET_CONTRAST 0x81u
#define CMD_SET_REMAP 0xA0u
#define CMD_SET_START_LINE 0xA1u
#define CMD_SET_OFFSET 0xA2u
#define CMD_MODE_NORMAL 0xA4u
#define CMD_SET_MULTIPLEX 0xA8u
#define CMD_FUNCTION_A 0xABu
#define CMD_DISPLAY_OFF 0xAEu
#define CMD_DISPLAY_ON 0xAFu
#define CMD_SET_PHASE 0xB1u
#define CMD_SET_CLOCK 0xB3u
#define CMD_DEFAULT_GRAYSCALE 0xB9u
#define CMD_SET_PRECHARGE 0xBCu
#define CMD_SET_VCOMH 0xBEu
#define CMD_COMMAND_LOCK 0xFDu

/* Power ON sequence, datasheet section 7.9:
 *  - RES# low for at least 100 us, then high
 *  - at least 100 us after RES# goes low before VCC comes up, which the module
 *    handles internally from its single 3.3 V rail
 *  - at least 50 ms after the supplies are stable before sending a command
 *  - SEG/COM are live 200 ms after AFh
 * The two reset figures are in microseconds and the expander's own I2C
 * transactions already take longer than that, so they are met by construction;
 * the millisecond waits are explicit. */
#define RESET_LOW_MS 1
#define SUPPLY_SETTLE_MS 50
#define DISPLAY_ON_MS 200

static spi_device_handle_t s_device[DISPLAY_COUNT];

static const uint8_t INIT_COMMANDS[] = {
    CMD_COMMAND_LOCK, 0x12,      /* unlock the command interface */
    CMD_DISPLAY_OFF,
    CMD_SET_CLOCK, 0xA0,         /* divider 1, oscillator at its default step */
    CMD_SET_MULTIPLEX, 0x3F,     /* 64 rows */
    CMD_SET_OFFSET, 0x00,
    CMD_SET_START_LINE, 0x00,
    /* A[1] nibble re-map and A[4] COM re-map on, matching the module's
     * physical orientation in the rail: the ribbon leaves at the bottom, so
     * the panel is mounted rotated relative to the controller's default scan. */
    CMD_SET_REMAP, 0x52,
    CMD_FUNCTION_A, 0x01,        /* enable the internal VDD regulator */
    CMD_SET_CONTRAST, 0x7F,      /* reset default; brightness is configurable */
    CMD_SET_PHASE, 0x11,
    CMD_DEFAULT_GRAYSCALE,
    CMD_SET_PRECHARGE, 0x04,
    CMD_SET_VCOMH, 0x05,
    CMD_MODE_NORMAL,
};

static esp_err_t set_data_mode(bool data)
{
    return expander_set(EXP_OLED_DC_PORT, EXP_OLED_DC_BIT, data);
}

static esp_err_t transmit(uint8_t display, const uint8_t *bytes, size_t length)
{
    spi_transaction_t transaction = {
        .length = length * 8u,
        .tx_buffer = bytes,
    };
    return spi_device_polling_transmit(s_device[display], &transaction);
}

/* Commands and data are separated deliberately: the D/C switch is an I2C
 * round trip, so one switch per batch rather than one per byte. */
static esp_err_t write_commands(uint8_t display, const uint8_t *bytes, size_t length)
{
    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device[display], portMAX_DELAY), TAG, "acquire");
    esp_err_t err = set_data_mode(false);
    if (err == ESP_OK) {
        err = transmit(display, bytes, length);
    }
    spi_device_release_bus(s_device[display]);
    return err;
}

esp_err_t display_write(uint8_t display, const uint8_t *data, size_t length)
{
    if (display >= DISPLAY_COUNT || data == NULL || length == 0u) {
        return ESP_ERR_INVALID_ARG;
    }
    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device[display], portMAX_DELAY), TAG, "acquire");
    esp_err_t err = set_data_mode(true);
    if (err == ESP_OK) {
        err = transmit(display, data, length);
    }
    /* Leave the line in command mode so a stray transfer is interpreted as a
     * command against a closed window rather than written into pixels. */
    if (err == ESP_OK) {
        err = set_data_mode(false);
    }
    spi_device_release_bus(s_device[display]);
    return err;
}

esp_err_t display_set_window(uint8_t display, uint8_t column_start, uint8_t column_end,
                             uint8_t row_start, uint8_t row_end)
{
    if (display >= DISPLAY_COUNT || column_end >= DISPLAY_COLUMNS ||
        row_end >= DISPLAY_ROWS || column_start > column_end || row_start > row_end) {
        return ESP_ERR_INVALID_ARG;
    }
    const uint8_t window[6] = {
        CMD_SET_COLUMN, column_start, column_end,
        CMD_SET_ROW, row_start, row_end,
    };
    return write_commands(display, window, sizeof(window));
}

esp_err_t display_clear(uint8_t display)
{
    ESP_RETURN_ON_ERROR(
        display_set_window(display, 0, DISPLAY_COLUMNS - 1u, 0, DISPLAY_ROWS - 1u),
        TAG, "clear window");

    /* One row at a time so no 8 KB frame buffer is needed, but one data-mode
     * switch for the whole panel: the D/C line is an I2C round trip, and
     * paying it per row would cost 128 of them. Static because the transfer
     * may run under DMA, and a static array is already zero. */
    static uint8_t blank[DISPLAY_COLUMNS];

    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device[display], portMAX_DELAY),
                        TAG, "acquire");
    esp_err_t err = set_data_mode(true);
    for (uint8_t row = 0; err == ESP_OK && row < DISPLAY_ROWS; row++) {
        err = transmit(display, blank, sizeof(blank));
    }
    /* Back to command mode either way; see display_write. */
    const esp_err_t restore = set_data_mode(false);
    spi_device_release_bus(s_device[display]);
    return (err != ESP_OK) ? err : restore;
}

esp_err_t display_set_on(uint8_t display, bool on)
{
    if (display >= DISPLAY_COUNT) {
        return ESP_ERR_INVALID_ARG;
    }
    const uint8_t command = on ? CMD_DISPLAY_ON : CMD_DISPLAY_OFF;
    return write_commands(display, &command, 1);
}

esp_err_t display_set_contrast(uint8_t display, uint8_t contrast)
{
    if (display >= DISPLAY_COUNT) {
        return ESP_ERR_INVALID_ARG;
    }
    const uint8_t command[2] = {CMD_SET_CONTRAST, contrast};
    return write_commands(display, command, sizeof(command));
}

esp_err_t display_init(void)
{
    static const int chip_selects[DISPLAY_COUNT] = {PIN_OLED1_CS_N, PIN_OLED2_CS_N};
    for (uint8_t display = 0; display < DISPLAY_COUNT; display++) {
        const spi_device_interface_config_t config = {
            .mode = 0,
            .clock_speed_hz = DISPLAY_CLOCK_HZ,
            .spics_io_num = chip_selects[display],
            .queue_size = 1,
        };
        ESP_RETURN_ON_ERROR(spi_bus_add_device(CHESSBOARD_SPI_HOST, &config, &s_device[display]),
                            TAG, "add device");
    }

    /* One reset line for both modules, so this is a pair operation. The
     * expander has held them in reset since boot. */
    ESP_RETURN_ON_ERROR(expander_set(EXP_OLED_RESET_N_PORT, EXP_OLED_RESET_N_BIT, false),
                        TAG, "reset assert");
    vTaskDelay(pdMS_TO_TICKS(RESET_LOW_MS));
    ESP_RETURN_ON_ERROR(expander_set(EXP_OLED_RESET_N_PORT, EXP_OLED_RESET_N_BIT, true),
                        TAG, "reset release");
    vTaskDelay(pdMS_TO_TICKS(SUPPLY_SETTLE_MS));

    for (uint8_t display = 0; display < DISPLAY_COUNT; display++) {
        ESP_RETURN_ON_ERROR(write_commands(display, INIT_COMMANDS, sizeof(INIT_COMMANDS)),
                            TAG, "init");
        ESP_RETURN_ON_ERROR(display_clear(display), TAG, "clear");
        ESP_RETURN_ON_ERROR(display_set_on(display, true), TAG, "on");
    }
    /* SEG and COM come up 200 ms after AFh; both were commanded above, so one
     * wait covers the pair. */
    vTaskDelay(pdMS_TO_TICKS(DISPLAY_ON_MS));

    ESP_LOGI(TAG, "%d displays up, %dx%d", DISPLAY_COUNT,
             DISPLAY_WIDTH_PIXELS, DISPLAY_HEIGHT_PIXELS);
    return ESP_OK;
}
