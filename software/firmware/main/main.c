/* Application wiring and the main loop. The only place that knows both core/
 * and port/ exist; see docs/software/architecture.md. */

#include <stdio.h>

#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "core/button.h"
#include "core/fault.h"
#include "core/game.h"
#include "core/hw/button.h"
#include "core/hw/clock.h"
#include "core/hw/output.h"
#include "core/hw/scan.h"
#include "core/hw/storage.h"
#include "core/identity.h"
#include "core/registry.h"
#include "core/snapshot.h"
#include "core/square.h"
#include "core/stability.h"
#include "port/board_hw.h"
#include "port/board_pins.h"
#include "port/display.h"
#include "port/expander.h"
#include "port/lightbar.h"
#include "port/matrix.h"
#include "port/pn5180.h"
#include "port/spi_bus.h"

static const char *TAG = "chessboard";

/* The idle gap between sweeps, not a scan rate: the sweep itself is dominated
 * by empty-slot timeouts (see SLOT_TIMEOUT_US in port/pn5180.c), so pausing
 * longer here buys energy, not correctness. */
#define SCAN_PERIOD_MS 250u

/* Owned at file scope rather than on the stack: the game alone carries a
 * position, a record and a derivation context, about 9 KB against the main
 * task's default 3.5 KB. */
static game_t s_game;
static button_t s_button;
static stability_t s_stability;
static piece_registry_t s_registry;
static board_snapshot_t s_raw;
static board_snapshot_t s_stable;

/* What the displays currently say about sensing, so a persisting fault is
 * written once rather than on every sweep. A fault found in a raw sweep
 * clears as soon as sweeps run clean again; a fault found in a stable
 * position stays until a stable position resolves cleanly. The game paints
 * nothing while a fault is up. */
static board_fault_report_t s_shown_fault;
static bool s_shown_from_sweep;

static bool init_step(const char *name, esp_err_t err)
{
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "%s init failed: %s", name, esp_err_to_name(err));
        return false;
    }
    return true;
}

static void display_fault(const board_fault_report_t *fault)
{
    /* The fault name, and the square when one is known: the fault table's
     * recovery instructions all start from which square to look at. The text
     * renderer upper-cases what it draws. */
    char message[32];
    if (square_is_valid(fault->square)) {
        snprintf(message, sizeof(message), "%s %c%u", board_fault_name(fault->fault),
                 square_file_letter(fault->square), (unsigned)square_rank(fault->square));
    } else {
        snprintf(message, sizeof(message), "%s", board_fault_name(fault->fault));
    }
    hw_output_display_text(PIECE_COLOR_WHITE, message);
    hw_output_display_text(PIECE_COLOR_BLACK, message);
}

static void show_fault(const board_fault_report_t *fault, bool from_sweep)
{
    if (s_shown_fault.fault != fault->fault || s_shown_fault.square != fault->square) {
        /* Logged as well as displayed: the serial log is the record a
         * session leaves behind. */
        if (square_is_valid(fault->square)) {
            ESP_LOGW(TAG, "fault %s at %c%u", board_fault_name(fault->fault),
                     square_file_letter(fault->square),
                     (unsigned)square_rank(fault->square));
        } else {
            ESP_LOGW(TAG, "fault %s board-wide", board_fault_name(fault->fault));
        }
        display_fault(fault);
        s_shown_fault = *fault;
    }
    s_shown_from_sweep = from_sweep;
}

static void clear_fault_display(void)
{
    if (s_shown_fault.fault == BOARD_FAULT_NONE) {
        return;
    }
    hw_output_display_text(PIECE_COLOR_WHITE, "");
    hw_output_display_text(PIECE_COLOR_BLACK, "");
    s_shown_fault.fault = BOARD_FAULT_NONE;
    s_shown_fault.square = SQUARE_INVALID;
}

/* One pass of the sensing pipeline: scan, stability, identity. Faults surface
 * on the displays; what comes back is what the game may consume this step. */
static void sweep_once(const board_snapshot_t **raw_clean,
                       const board_snapshot_t **stable)
{
    *raw_clean = NULL;
    *stable = NULL;

    if (!hw_scan_board(&s_raw)) {
        /* board_hw already logged the reason; the next sweep retries. */
        return;
    }

    if (s_raw.fault.fault != BOARD_FAULT_NONE) {
        /* A faulted sweep never reaches stability (it is not evidence), so it
         * is reported from here. Feeding it in anyway is what resets the
         * agreement count, exactly as the stability contract requires. */
        show_fault(&s_raw.fault, true);
        (void)stability_update(&s_stability, &s_raw, hw_clock_now_ms(), &s_stable);
        return;
    }

    if (s_shown_fault.fault != BOARD_FAULT_NONE && s_shown_from_sweep) {
        /* The condition the displays reported is gone. */
        clear_fault_display();
    }
    *raw_clean = &s_raw;

    const bool emitted =
        stability_update(&s_stability, &s_raw, hw_clock_now_ms(), &s_stable);

    square_t unstable = SQUARE_INVALID;
    if (stability_unstable_square(&s_stability, &unstable)) {
        /* Flicker is only visible across sweeps, so it can never appear
         * inside a snapshot; this is the one fault raised here. */
        const board_fault_report_t fault = {BOARD_FAULT_SQUARE_UNSTABLE, unstable};
        show_fault(&fault, true);
        return;
    }

    if (!emitted) {
        return;
    }

    if (!identity_resolve(&s_registry, &s_stable)) {
        /* Unknown or duplicated tags name a stable position, so the report
         * stays up until a stable position resolves cleanly. */
        show_fault(&s_stable.fault, false);
        return;
    }

    clear_fault_display();
    *stable = &s_stable;
    ESP_LOGI(TAG, "stable position, %u squares occupied",
             (unsigned)board_snapshot_occupied_count(&s_stable));
}

void app_main(void)
{
    ESP_LOGI(TAG, "chessboard firmware, reader CS on GPIO%d, I2C on %d/%d",
             PIN_NFC_CS_N, PIN_I2C_SCL, PIN_I2C_SDA);

    /* Before anything else: until the expander is configured the reader and
     * both displays are floating rather than held in reset. Nothing can run
     * without it, so this one alone is allowed to abort the boot. */
    ESP_ERROR_CHECK(expander_init());

    /* The scan path, in dependency order (see docs/software/architecture.md).
     * A board that cannot scan is still a board that can say so, which is why
     * these log and disable scanning instead of reboot-looping into a panic
     * no one is watching. */
    bool scan_ok = init_step("spi bus", spi_bus_init());
    scan_ok = scan_ok && init_step("matrix", matrix_init());
    scan_ok = scan_ok && init_step("reader", pn5180_init());

    /* Output surfaces. Losing one loses feedback, not the game; every later
     * write through hw_output_* reports its own failure. */
    (void)init_step("display", display_init());
    (void)init_step("lightbar", lightbar_init());

    /* Persistence. A registry that is missing, unsealed or corrupt is treated
     * as no registry: every piece then reads as TAG_FAULT, which is the
     * honest state of an unprovisioned board. */
    if (!init_step("storage", board_hw_storage_init()) ||
        !hw_storage_load_registry(&s_registry)) {
        registry_init(&s_registry);
    }

    stability_init(&s_stability);
    button_init(&s_button);
    game_init(&s_game);
    if (s_game.state == GAME_STATE_PLAYING) {
        ESP_LOGI(TAG, "stored game loaded, %u plies, awaiting a matching board",
                 (unsigned)s_game.record.ply_count);
    }

    if (!scan_ok) {
        hw_output_display_text(PIECE_COLOR_WHITE, "SCAN FAULT");
        hw_output_display_text(PIECE_COLOR_BLACK, "SCAN FAULT");
    }

    while (true) {
        const uint32_t now_ms = hw_clock_now_ms();
        const button_event_t button =
            button_update(&s_button, hw_button_pressed(), now_ms);

        const board_snapshot_t *raw_clean = NULL;
        const board_snapshot_t *stable = NULL;
        if (scan_ok) {
            sweep_once(&raw_clean, &stable);
        }

        game_step(&s_game, raw_clean, stable, button,
                  s_shown_fault.fault != BOARD_FAULT_NONE, now_ms);

        vTaskDelay(pdMS_TO_TICKS(SCAN_PERIOD_MS));
    }
}
