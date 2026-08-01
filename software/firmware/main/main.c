/* Application wiring. The only place that knows both core/ and port/ exist;
 * see docs/software/architecture.md. */

#include "esp_err.h"
#include "esp_log.h"
#include "esp_timer.h"

#include "core/engine.h"
#include "core/hw/clock.h"
#include "core/snapshot.h"
#include "port/board_pins.h"
#include "port/expander.h"
#include "port/matrix.h"
#include "port/pn5180.h"
#include "port/spi_bus.h"

static const char *TAG = "chessboard";

uint32_t hw_clock_now_ms(void)
{
    return (uint32_t)(esp_timer_get_time() / 1000);
}

void app_main(void)
{
    ESP_LOGI(TAG, "chessboard firmware, reader CS on GPIO%d, I2C on %d/%d",
             PIN_NFC_CS_N, PIN_I2C_SCL, PIN_I2C_SDA);

    /* Before anything else: until the expander is configured the reader and
     * both displays are floating rather than held in reset. */
    ESP_ERROR_CHECK(expander_init());

    /* The matrix registers power up driving an undefined selection and cannot
     * be blanked, so putting a known pattern on them is the next thing done. */
    ESP_ERROR_CHECK(spi_bus_init());
    ESP_ERROR_CHECK(matrix_init());

    /* Reader last of the three, because its reset line runs through the
     * expander and its liveness check needs the bus already up. */
    ESP_ERROR_CHECK(pn5180_init());

    engine_state_t engine;
    engine_init(&engine);
    ESP_LOGW(TAG, "rules engine is a stub: %s",
             engine_is_implemented() ? "implemented" : "not implemented");
}
