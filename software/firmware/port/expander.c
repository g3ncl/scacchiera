#include "port/expander.h"

#include "driver/i2c_master.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "port/board_pins.h"
#include "port/expander_config.h"

static const char *TAG = "expander";

/* TCA9535 register map, datasheet section 8.6. Configuration and both output
 * registers power up as 1111 1111; the input registers read the pins. */
#define REG_INPUT_0 0x00u
#define REG_OUTPUT_0 0x02u
#define REG_POLARITY_0 0x04u
#define REG_CONFIG_0 0x06u

#define I2C_TIMEOUT_MS 100
#define I2C_SPEED_HZ 400000

static i2c_master_bus_handle_t s_bus;
static i2c_master_dev_handle_t s_device;

/* The output registers are write-mostly and a read-modify-write per bit would
 * be three transactions and a race. Shadow them instead. */
static uint8_t s_output_shadow[2];

static esp_err_t write_register(uint8_t reg, uint8_t value)
{
    const uint8_t frame[2] = {reg, value};
    return i2c_master_transmit(s_device, frame, sizeof(frame), I2C_TIMEOUT_MS);
}

static esp_err_t read_register(uint8_t reg, uint8_t *value)
{
    return i2c_master_transmit_receive(s_device, &reg, 1, value, 1, I2C_TIMEOUT_MS);
}

esp_err_t expander_init(void)
{
    const i2c_master_bus_config_t bus_config = {
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .i2c_port = I2C_NUM_0,
        .scl_io_num = PIN_I2C_SCL,
        .sda_io_num = PIN_I2C_SDA,
        .glitch_ignore_cnt = 7,
        /* The hub carries 4.7 k bus pullups, and they are what hold IO8 and
         * IO9 high for SPI boot. Enabling the weak internal pullups on top of
         * them would change the bus rise time for no reason. */
        .flags = {.enable_internal_pullup = false},
    };
    ESP_RETURN_ON_ERROR(i2c_new_master_bus(&bus_config, &s_bus), TAG, "i2c bus");

    const i2c_device_config_t device_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = EXPANDER_I2C_ADDRESS,
        .scl_speed_hz = I2C_SPEED_HZ,
    };
    ESP_RETURN_ON_ERROR(i2c_master_bus_add_device(s_bus, &device_config, &s_device),
                        TAG, "i2c device");

    /* Order matters and is the whole point of this function.
     *
     * At power-on every pin is an input and both output registers hold
     * 1111 1111. Writing the configuration first would make five pins outputs
     * driving high in the same instant: the reader and both displays would
     * come out of reset at an uncontrolled moment, the light-bar rail would
     * switch on at up to 448 mA, and SEL_RCLK would rise against its 100 k
     * pulldown, latching whatever random bits the matrix shift registers hold
     * into their outputs.
     *
     * So the safe values go in while the pins are still high impedance, and
     * only then do they become outputs. */
    s_output_shadow[0] = EXPANDER_OUTPUT_PORT_0_SAFE;
    s_output_shadow[1] = EXPANDER_OUTPUT_PORT_1_SAFE;
    ESP_RETURN_ON_ERROR(write_register(REG_OUTPUT_0, s_output_shadow[0]), TAG, "output 0");
    ESP_RETURN_ON_ERROR(write_register(REG_OUTPUT_0 + 1u, s_output_shadow[1]), TAG, "output 1");

    /* Polarity inversion stays off. The active-low signals here are named with
     * a _N suffix and inverted in the code that reads them, so that a reader
     * of this driver is never wondering whether a bit has been flipped twice. */
    ESP_RETURN_ON_ERROR(write_register(REG_POLARITY_0, 0x00u), TAG, "polarity 0");
    ESP_RETURN_ON_ERROR(write_register(REG_POLARITY_0 + 1u, 0x00u), TAG, "polarity 1");

    ESP_RETURN_ON_ERROR(write_register(REG_CONFIG_0, EXPANDER_CONFIG_PORT_0), TAG, "config 0");
    ESP_RETURN_ON_ERROR(write_register(REG_CONFIG_0 + 1u, EXPANDER_CONFIG_PORT_1), TAG, "config 1");

    ESP_LOGI(TAG, "TCA9535 at 0x%02x ready, outputs safe", EXPANDER_I2C_ADDRESS);
    return ESP_OK;
}

esp_err_t expander_set(uint8_t port, uint8_t bit, bool level)
{
    if (port > 1u || bit > 7u) {
        return ESP_ERR_INVALID_ARG;
    }
    const uint8_t mask = (uint8_t)(1u << bit);
    const uint8_t updated = level ? (uint8_t)(s_output_shadow[port] | mask)
                                  : (uint8_t)(s_output_shadow[port] & (uint8_t)~mask);
    if (updated == s_output_shadow[port]) {
        return ESP_OK;
    }
    ESP_RETURN_ON_ERROR(write_register((uint8_t)(REG_OUTPUT_0 + port), updated), TAG, "set");
    s_output_shadow[port] = updated;
    return ESP_OK;
}

esp_err_t expander_get(uint8_t port, uint8_t bit, bool *level)
{
    if (port > 1u || bit > 7u || level == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    uint8_t value = 0;
    ESP_RETURN_ON_ERROR(read_register((uint8_t)(REG_INPUT_0 + port), &value), TAG, "get");
    *level = (value & (uint8_t)(1u << bit)) != 0u;
    return ESP_OK;
}

esp_err_t expander_pulse(uint8_t port, uint8_t bit)
{
    /* Two I2C transactions at 400 kHz put roughly 50 us between the edges,
     * far longer than the 74HC595's nanosecond-scale pulse width, so no delay
     * is needed to make the edge legal. */
    ESP_RETURN_ON_ERROR(expander_set(port, bit, false), TAG, "pulse low");
    ESP_RETURN_ON_ERROR(expander_set(port, bit, true), TAG, "pulse high");
    return expander_set(port, bit, false);
}
