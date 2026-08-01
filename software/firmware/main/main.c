/* Application wiring. The only place that knows both core/ and port/ exist;
 * see docs/software/architecture.md. */

#include "esp_log.h"
#include "esp_timer.h"

#include "core/engine.h"
#include "core/hw/clock.h"
#include "core/snapshot.h"
#include "port/board_pins.h"

static const char *TAG = "chessboard";

uint32_t hw_clock_now_ms(void)
{
    return (uint32_t)(esp_timer_get_time() / 1000);
}

void app_main(void)
{
    ESP_LOGI(TAG, "chessboard firmware, reader CS on GPIO%d, I2C on %d/%d",
             PIN_NFC_CS_N, PIN_I2C_SCL, PIN_I2C_SDA);

    engine_state_t engine;
    engine_init(&engine);
    ESP_LOGW(TAG, "rules engine is a stub: %s",
             engine_is_implemented() ? "implemented" : "not implemented");
}
