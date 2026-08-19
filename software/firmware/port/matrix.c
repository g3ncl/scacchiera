#include "port/matrix.h"

#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"

#include "port/board_pins.h"
#include "port/expander.h"
#include "port/matrix_encoding.h"
#include "port/spi_bus.h"

static const char *TAG = "matrix";

/* 1 MHz, set by the interconnect rather than the part. The registers sit at
 * the far end of an unterminated 7-way cable to a 300 mm board, and 32 bits
 * still take only 32 us. The 74HC595's own limit is far above this; the
 * datasheet characterises 2.0, 4.5 and 6.0 V and the rail here is 3.3 V, so
 * quoting an exact fmax would mean interpolating a figure the design does not
 * need. */
#define MATRIX_CLOCK_HZ 1000000

static spi_device_handle_t s_device;

static esp_err_t shift_and_latch(uint32_t pattern)
{
    /* MSB first, so the first byte clocked out travels furthest along the
     * chain and settles in board 3. See matrix_encoding.h. */
    const uint8_t frame[4] = {
        (uint8_t)(pattern >> 24),
        (uint8_t)((pattern >> 16) & 0xFFu),
        (uint8_t)((pattern >> 8) & 0xFFu),
        (uint8_t)(pattern & 0xFFu),
    };
    spi_transaction_t transaction = {
        .length = 32,
        .tx_buffer = frame,
    };

    /* Hold the bus across both the shift and the latch. The latch goes out
     * over I2C and takes tens of microseconds, and any display or reader
     * transfer slipping into that gap would be shifted into these registers
     * and then committed by our own latch edge. */
    ESP_RETURN_ON_ERROR(spi_device_acquire_bus(s_device, portMAX_DELAY), TAG, "acquire");

    esp_err_t err = spi_device_polling_transmit(s_device, &transaction);
    if (err == ESP_OK) {
        err = expander_pulse(EXP_SEL_RCLK_PORT, EXP_SEL_RCLK_BIT);
    }

    spi_device_release_bus(s_device);
    return err;
}

esp_err_t matrix_init(void)
{
    const spi_device_interface_config_t config = {
        /* Mode 0: the 74HC595 shifts on the rising edge of SHCP. */
        .mode = 0,
        .clock_speed_hz = MATRIX_CLOCK_HZ,
        /* No chip select exists on these registers. This is the reason every
         * other transfer on this bus is also clocked into them. */
        .spics_io_num = -1,
        .queue_size = 1,
    };
    ESP_RETURN_ON_ERROR(spi_bus_add_device(CHESSBOARD_SPI_HOST, &config, &s_device),
                        TAG, "add device");

    /* The first thing that happens, and it cannot be skipped: the registers
     * power up holding nothing in particular with their outputs already
     * driving, and there is no clear line to blank them. */
    ESP_RETURN_ON_ERROR(shift_and_latch(MATRIX_PATTERN_NONE), TAG, "initial deselect");
    ESP_LOGI(TAG, "%d lines deselected", MATRIX_LINE_COUNT);
    return ESP_OK;
}

esp_err_t matrix_select(uint8_t line)
{
    if (line >= MATRIX_LINE_COUNT) {
        return ESP_ERR_INVALID_ARG;
    }
    return shift_and_latch(matrix_pattern_for_line(line));
}

esp_err_t matrix_deselect_all(void)
{
    return shift_and_latch(MATRIX_PATTERN_NONE);
}
