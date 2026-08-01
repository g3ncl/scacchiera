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
#include "core/hw/scan.h"
#include "core/scan_join.h"
#include "core/text.h"
#include "core/hw/output.h"
#include "core/hw/storage.h"
#include "port/display.h"
#include "port/matrix.h"
#include "port/pn5180.h"
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

/* One text line, scaled to fill the 64-pixel height. A 7-pixel glyph at scale
 * 6 is 42 pixels tall, which reads across a table without crowding the edges.
 * The band is the glyph height plus its blank row, times the scale. */
#define TEXT_SCALE 6
#define TEXT_BAND_ROWS (FONT_CELL_HEIGHT * TEXT_SCALE)
#define TEXT_BAND_COLUMNS DISPLAY_COLUMNS

static uint8_t s_text_band[TEXT_BAND_COLUMNS * TEXT_BAND_ROWS];

void hw_output_display_text(piece_color_t side, const char *text)
{
    if (side >= DISPLAY_COUNT) {
        return;
    }
    const char *message = (text != NULL) ? text : "";

    const text_canvas_t canvas = {
        .pixels = s_text_band,
        .columns = TEXT_BAND_COLUMNS,
        .rows = TEXT_BAND_ROWS,
    };
    text_clear(&canvas);

    /* Centred, and clamped rather than negative when a message is too long to
     * fit: an overlong string truncates at the right edge instead of starting
     * off-screen and losing its beginning. */
    const uint16_t width = text_width(message, TEXT_SCALE);
    const uint16_t x = (width < DISPLAY_WIDTH_PIXELS)
                           ? (uint16_t)((DISPLAY_WIDTH_PIXELS - width) / 2u)
                           : 0u;
    text_draw(&canvas, x, 0, message, TEXT_SCALE, 0x0F);

    /* Vertically centred band, so the rows above and below stay as the clear
     * left them rather than needing a full-frame rewrite. */
    const uint8_t top = (uint8_t)((DISPLAY_ROWS - TEXT_BAND_ROWS) / 2u);
    esp_err_t err = display_set_window((uint8_t)side, 0, DISPLAY_COLUMNS - 1u,
                                       top, (uint8_t)(top + TEXT_BAND_ROWS - 1u));
    if (err == ESP_OK) {
        err = display_write((uint8_t)side, s_text_band, sizeof(s_text_band));
    }
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "display %d text failed: %s", (int)side, esp_err_to_name(err));
    }
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

/* One complete sweep: eight rows then eight columns, one single-slot inventory
 * per line, joined into squares by core/scan_join.c.
 *
 * The RF field stays on for the whole sweep rather than being cycled per line.
 * Switching a line is a shift and a latch on the matrix, which does not
 * disturb the reader, and cycling the field sixteen times would dominate the
 * scan time for nothing. */
static esp_err_t sweep_lines(uint8_t first_line, uint8_t count, line_reading_t *out)
{
    for (uint8_t index = 0; index < count; index++) {
        ESP_RETURN_ON_ERROR(matrix_select((uint8_t)(first_line + index)), TAG, "select");

        uint8_t found = 0;
        bool incomplete = false;
        ESP_RETURN_ON_ERROR(
            pn5180_iso15693_inventory_16(out[index].uids, SCAN_MAX_TAGS_PER_LINE,
                                         &found, &incomplete),
            TAG, "inventory");
        out[index].count = found;
        out[index].incomplete = incomplete;
    }
    return ESP_OK;
}

bool hw_scan_board(board_snapshot_t *snapshot)
{
    /* Static rather than automatic: sixteen lines of eight UIDs is about a
     * kilobyte, which is a large fraction of a default task stack. */
    static line_reading_t rows[SCAN_ROWS];
    static line_reading_t columns[SCAN_COLUMNS];
    memset(rows, 0, sizeof(rows));
    memset(columns, 0, sizeof(columns));

    if (pn5180_load_rf_config(PN5180_RF_TX_ISO15693_ASK100_26,
                              PN5180_RF_RX_ISO15693_26) != ESP_OK) {
        return false;
    }
    if (pn5180_rf_field(true) != ESP_OK) {
        return false;
    }

    esp_err_t err = sweep_lines(0, SCAN_ROWS, rows);
    if (err == ESP_OK) {
        err = sweep_lines(SCAN_ROWS, SCAN_COLUMNS, columns);
    }

    /* Field off and every line deselected before returning, whatever happened.
     * Leaving one antenna biased and the field up would keep drawing current
     * between scans and leave the board in a state the next sweep has to undo. */
    (void)pn5180_rf_field(false);
    (void)matrix_deselect_all();

    if (err != ESP_OK) {
        ESP_LOGW(TAG, "sweep failed: %s", esp_err_to_name(err));
        return false;
    }

    scan_join(rows, columns, snapshot);
    return true;
}
