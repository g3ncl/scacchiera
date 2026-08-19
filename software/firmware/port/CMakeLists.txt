# ESP-IDF only. Everything here touches ESP-IDF headers by definition, so the
# host gate does not build it; the fakes in test/ stand in for it instead.
idf_component_register(
  SRCS "expander.c" "spi_bus.c" "matrix.c" "pn5180.c" "display.c" "lightbar.c" "board_hw.c"
  INCLUDE_DIRS "." ".."
  REQUIRES driver esp_timer esp_driver_rmt nvs_flash esp_driver_gpio esp_driver_i2c esp_driver_spi core
)
