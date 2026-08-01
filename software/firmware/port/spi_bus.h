#ifndef CHESSBOARD_PORT_SPI_BUS_H
#define CHESSBOARD_PORT_SPI_BUS_H

#include "driver/spi_master.h"
#include "esp_err.h"

/* One SPI bus, four devices on it: the PN5180, both displays, and the matrix
 * selection registers. The registers are the awkward one because they have no
 * chip select and see every edge on the bus; see port/matrix.h. */

#define CHESSBOARD_SPI_HOST SPI2_HOST

esp_err_t spi_bus_init(void);

#endif
