/* The target's side of the core/hw boundary.
 *
 * These are the four free functions core/ declares and test/ fakes: the clock,
 * the output surface, persistence, and the board scan. Nothing in core/ knows
 * this file exists, which is what lets the same rules run on a host with
 * deterministic fakes underneath. */

#include <string.h>

#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "nvs.h"
#include "nvs_flash.h"

#include "core/hw/clock.h"
#include "core/hw/output.h"
#include "core/hw/storage.h"
#include "port/display.h"
#include "port/lightbar.h"

static const char *TAG = "board_hw";

#define NVS_NAMESPACE "chessboard"
#define NVS_SNAPSHOT_KEY "snapshot"

uint32_t hw_clock_now_ms(void)
{
    return (uint32_t)(esp_timer_get_time() / 1000);
}

/* Cue colours. Red for the illegal-position flash is the one that matters:
 * docs/functional/gameplay.md requires the offending side to flash red, and
 * the Harvatek part takes red first, so this is where a wrong colour order
 * would show. port/lightbar_encoding.h carries the test for that. */
static void cue_colour(light_cue_t cue, uint8_t *red, uint8_t *green, uint8_t *blue)
{
    switch (cue) {
    case LIGHT_CUE_MOVE_ACCEPTED: *red = 0; *green = 40; *blue = 0; break;
    case LIGHT_CUE_ILLEGAL: *red = 60; *green = 0; *blue = 0; break;
    case LIGHT_CUE_RESULT: *red = 40; *green = 40; *blue = 40; break;
    case LIGHT_CUE_WIFI: *red = 0; *green = 0; *blue = 40; break;
    case LIGHT_CUE_COUNTDOWN: *red = 50; *green = 25; *blue = 0; break;
    case LIGHT_CUE_NONE:
    default: *red = 0; *green = 0; *blue = 0; break;
    }
}

void hw_output_light_cue(piece_color_t side, light_cue_t cue)
{
    uint8_t red = 0;
    uint8_t green = 0;
    uint8_t blue = 0;
    cue_colour(cue, &red, &green, &blue);
    /* One bar per side, and the bar index matches the colour enum because
     * white is 0 in both. */
    lightbar_set_bar((uint8_t)side, red, green, blue);
    const esp_err_t err = lightbar_show();
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "light cue not shown: %s", esp_err_to_name(err));
    }
}

void hw_output_display_text(piece_color_t side, const char *text)
{
    /* Not yet rendered. The display driver can address any window and push
     * pixels, but there is no glyph source, so text cannot become pixels here
     * without inventing a font inline. The next display increment generates
     * one the way board_pins.h is generated, rather than hand-typing a table.
     *
     * Logging rather than silently dropping, so a caller can see its text
     * reaching the boundary and V6 has something to assert on before the font
     * exists. */
    ESP_LOGI(TAG, "display %d: %s", (int)side, text != NULL ? text : "(null)");
}

/* Persistence for the in-progress snapshot. NVS rather than the SPIFFS games
 * partition because this is rewritten after every committed move and NVS
 * wear-levels; PGN goes to the file partition instead. */

static esp_err_t open_nvs(nvs_open_mode_t mode, nvs_handle_t *handle)
{
    return nvs_open(NVS_NAMESPACE, mode, handle);
}

bool hw_storage_save_snapshot(const board_snapshot_t *snapshot)
{
    nvs_handle_t handle;
    if (open_nvs(NVS_READWRITE, &handle) != ESP_OK) {
        return false;
    }
    esp_err_t err = nvs_set_blob(handle, NVS_SNAPSHOT_KEY, snapshot, sizeof(*snapshot));
    if (err == ESP_OK) {
        /* Commit before reporting success. NVS buffers writes, and a caller
         * that believes a snapshot is durable when it is still in RAM would
         * lose the move it just committed on a brownout. */
        err = nvs_commit(handle);
    }
    nvs_close(handle);
    return err == ESP_OK;
}

bool hw_storage_load_snapshot(board_snapshot_t *snapshot)
{
    nvs_handle_t handle;
    if (open_nvs(NVS_READONLY, &handle) != ESP_OK) {
        return false;
    }
    size_t length = sizeof(*snapshot);
    const esp_err_t err = nvs_get_blob(handle, NVS_SNAPSHOT_KEY, snapshot, &length);
    nvs_close(handle);
    /* A short or long blob is a layout change across a firmware update, not a
     * usable position. Refusing it here turns that into a clean resync prompt
     * rather than a garbled board. */
    return err == ESP_OK && length == sizeof(*snapshot);
}

bool hw_storage_clear(void)
{
    nvs_handle_t handle;
    if (open_nvs(NVS_READWRITE, &handle) != ESP_OK) {
        return false;
    }
    esp_err_t err = nvs_erase_key(handle, NVS_SNAPSHOT_KEY);
    if (err == ESP_ERR_NVS_NOT_FOUND) {
        err = ESP_OK;
    }
    if (err == ESP_OK) {
        err = nvs_commit(handle);
    }
    nvs_close(handle);
    return err == ESP_OK;
}

esp_err_t board_hw_storage_init(void)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        /* A partition that cannot be mounted is erased rather than left
         * broken: losing an in-progress game is recoverable, refusing to boot
         * is not. */
        ESP_LOGW(TAG, "NVS unusable, erasing");
        ESP_RETURN_ON_ERROR(nvs_flash_erase(), TAG, "nvs erase");
        err = nvs_flash_init();
    }
    return err;
}
