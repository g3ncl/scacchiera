#include "port/spi_bus.h"

#include "esp_check.h"

#include "port/board_pins.h"
#include "port/display.h"

static const char *TAG = "spi";

esp_err_t spi_bus_init(void)
{
    const spi_bus_config_t config = {
        .mosi_io_num = PIN_MOSI,
        .miso_io_num = PIN_MISO,
        .sclk_io_num = PIN_SCLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        /* A display frame is the largest single transfer on this bus, and the
         * driver pushes a whole window in one transaction. ESP-IDF rejects any
         * transfer longer than this outright, so sizing it from the reader
         * instead would fail the first time text reached a panel. */
        .max_transfer_sz = DISPLAY_FRAME_BYTES,
    };
    ESP_RETURN_ON_ERROR(spi_bus_initialize(CHESSBOARD_SPI_HOST, &config, SPI_DMA_CH_AUTO),
                        TAG, "bus init");
    return ESP_OK;
}
