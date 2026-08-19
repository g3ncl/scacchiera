#include "port/lightbar.h"

#include <string.h>

#include "driver/rmt_encoder.h"
#include "driver/rmt_tx.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "port/board_pins.h"
#include "port/expander.h"

static const char *TAG = "lightbar";

/* 10 MHz gives 100 ns per tick, which divides every timing below exactly. */
#define RMT_RESOLUTION_HZ 10000000
#define TICKS_PER_100NS 1

/* Harvatek T37K3RGB datasheet, data transfer protocol table. These are not the
 * WS2812 numbers: the symbol period is 1200 ns split 300/900 rather than
 * 1250 ns split 400/850, and the reset is 200 us rather than 50 us. */
#define T0H_TICKS 3  /* 300 ns typical, 250 to 350 permitted */
#define T0L_TICKS 9  /* 900 ns typical */
#define T1H_TICKS 9  /* 900 ns typical */
#define T1L_TICKS 3  /* 300 ns typical */
#define RESET_GAP_US 250 /* above the datasheet's ">200 us" latch minimum */

static rmt_channel_handle_t s_channel;
static rmt_encoder_handle_t s_encoder;
static uint8_t s_stream[LIGHTBAR_STREAM_BYTES];

esp_err_t lightbar_set_bar(uint8_t bar, uint8_t red, uint8_t green, uint8_t blue)
{
    if (bar >= LIGHTBAR_BAR_COUNT) {
        return ESP_ERR_INVALID_ARG;
    }
    const uint8_t first = (uint8_t)(bar * LIGHTBAR_PIXELS_PER_BAR);
    for (uint8_t offset = 0; offset < LIGHTBAR_PIXELS_PER_BAR; offset++) {
        lightbar_pack(s_stream, (uint8_t)(first + offset), red, green, blue);
    }
    return ESP_OK;
}

void lightbar_clear(void)
{
    memset(s_stream, 0, sizeof(s_stream));
}

esp_err_t lightbar_show(void)
{
    const rmt_transmit_config_t config = {.loop_count = 0};
    ESP_RETURN_ON_ERROR(
        rmt_transmit(s_channel, s_encoder, s_stream, sizeof(s_stream), &config),
        TAG, "transmit");
    ESP_RETURN_ON_ERROR(rmt_tx_wait_all_done(s_channel, portMAX_DELAY), TAG, "wait");
    /* The chain latches on >200 us of idle line and nothing else produces
     * that gap: the encoder describes only bit symbols, so a second frame
     * started too soon reads as a continuation of the first and is forwarded
     * off the end of the chain. Holding the line idle here is what turns
     * "shown" from a hope into a guarantee. */
    esp_rom_delay_us(RESET_GAP_US);
    return ESP_OK;
}

esp_err_t lightbar_set_rail(bool on)
{
    return expander_set(EXP_LED_EN_PORT, EXP_LED_EN_BIT, on);
}

esp_err_t lightbar_rail_faulted(bool *faulted)
{
    if (faulted == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    bool level = false;
    ESP_RETURN_ON_ERROR(expander_get(EXP_LED_FAULT_N_PORT, EXP_LED_FAULT_N_BIT, &level),
                        TAG, "fault");
    /* Active low: the limiter pulls it down when it has latched off. */
    *faulted = !level;
    return ESP_OK;
}

esp_err_t lightbar_init(void)
{
    const rmt_tx_channel_config_t channel_config = {
        .gpio_num = PIN_LED_DATA,
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = RMT_RESOLUTION_HZ,
        .mem_block_symbols = 64,
        .trans_queue_depth = 2,
    };
    ESP_RETURN_ON_ERROR(rmt_new_tx_channel(&channel_config, &s_channel), TAG, "channel");

    /* A plain bytes encoder carries the whole protocol: the part has no
     * framing beyond back-to-back bit symbols, MSB first, then a reset gap. */
    const rmt_bytes_encoder_config_t encoder_config = {
        .bit0 = {
            .level0 = 1, .duration0 = T0H_TICKS,
            .level1 = 0, .duration1 = T0L_TICKS,
        },
        .bit1 = {
            .level0 = 1, .duration0 = T1H_TICKS,
            .level1 = 0, .duration1 = T1L_TICKS,
        },
        .flags = {.msb_first = 1},
    };
    ESP_RETURN_ON_ERROR(rmt_new_bytes_encoder(&encoder_config, &s_encoder), TAG, "encoder");
    ESP_RETURN_ON_ERROR(rmt_enable(s_channel), TAG, "enable");

    /* Blank first, rail second. Bringing the rail up before the pixels hold a
     * known value would show whatever the LEDs powered up with. */
    lightbar_clear();
    ESP_RETURN_ON_ERROR(lightbar_show(), TAG, "initial blank");
    ESP_RETURN_ON_ERROR(lightbar_set_rail(true), TAG, "rail on");

    ESP_LOGI(TAG, "%d pixels across %d bars", LIGHTBAR_PIXEL_COUNT, LIGHTBAR_BAR_COUNT);
    return ESP_OK;
}
