# ESP-IDF only. Everything here touches ESP-IDF headers by definition, so the
# host gate does not build it; the fakes in test/ stand in for it instead.
idf_component_register(
  SRCS "expander.c"
  INCLUDE_DIRS "." ".."
  REQUIRES driver esp_driver_gpio esp_driver_i2c esp_driver_spi core
)
