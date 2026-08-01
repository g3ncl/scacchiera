PYTHON := .venv/bin/python
XDG_DATA_HOME := $(CURDIR)/.cache/data
XDG_CACHE_HOME := $(CURDIR)/.cache/cache
XDG_CONFIG_HOME := $(CURDIR)/.cache/config
MPLCONFIGDIR := $(CURDIR)/.cache/matplotlib
PYTHONHASHSEED := 0
KICAD9_SYMBOL_DIR := $(HOME)/.local/share/flatpak/runtime/org.kicad.KiCad.Library.Symbols/x86_64/stable/active/files/symbols
KICAD_FOOTPRINT_DIR := $(HOME)/.local/share/flatpak/runtime/org.kicad.KiCad.Library.Footprints/x86_64/stable/active/files/footprints
KICAD_CLI := /usr/bin/kicad-cli

export XDG_DATA_HOME
export XDG_CACHE_HOME
export XDG_CONFIG_HOME
export MPLCONFIGDIR
export PYTHONHASHSEED
export KICAD9_SYMBOL_DIR
export KICAD_FOOTPRINT_DIR

.PHONY: check footprints schematic-lightbar schematic-matrix schematic-hub \
	pcb-lightbar pcb-lightbar-drc pcb-lightbar-fab \
	pcb-matrix pcb-matrix-route pcb-matrix-reroute pcb-matrix-drc pcb-matrix-fab \
	pcb-hub pcb-hub-route pcb-hub-reroute pcb-hub-drc pcb-hub-fab \
	pcb-power pcb-power-reroute pcb-power-drc pcb-power-fab power-rail-fit panel pcb-fab \
	firmware firmware-test firmware-pins firmware-target clean

check: pcb-lightbar-drc pcb-matrix-drc pcb-hub-drc pcb-power-drc firmware-test
	$(PYTHON) -m mypy hardware
	$(PYTHON) -m pytest

# Host firmware gate for V5. Warnings are errors, gcc's analyzer runs, and
# the sanitizers are enabled when their runtimes are installed.
FIRMWARE_DIR := software/firmware
FIRMWARE_BUILD := $(FIRMWARE_DIR)/build

# Regenerate the firmware pin map from the hub netlist. Run after any hub
# schematic change; test_firmware_pins.py fails if the committed copy drifts.
firmware-pins:
	$(PYTHON) -m hardware.pcb.firmware_pins

firmware:
	cmake -S $(FIRMWARE_DIR) -B $(FIRMWARE_BUILD) -DCMAKE_BUILD_TYPE=Debug
	cmake --build $(FIRMWARE_BUILD)

firmware-test: firmware
	ctest --test-dir $(FIRMWARE_BUILD) --output-on-failure

# The ESP32-C6 image. Not part of `check`, because it needs ESP-IDF exported
# and that is a 2 GB toolchain rather than a checkout dependency.
IDF_EXPORT ?= $(HOME)/esp/esp-idf-v5.5.5/export.sh

firmware-target: firmware-pins
	bash -c '. $(IDF_EXPORT) >/dev/null && cd $(FIRMWARE_DIR)/target && idf.py build'

schematic-lightbar: footprints
	$(PYTHON) -m hardware.pcb.generate lightbar

schematic-matrix: footprints
	$(PYTHON) -m hardware.pcb.generate matrix

schematic-hub: footprints
	$(PYTHON) -m hardware.pcb.generate hub

schematic-power: footprints
	$(PYTHON) -m hardware.pcb.generate power

footprints:
	$(PYTHON) -m hardware.pcb.footprints

# Normal builds import the reviewed route. A fresh autorouter run is an
# explicit operation because its result must pass review before replacing it.
pcb-matrix: schematic-matrix
	/usr/bin/python3 -m hardware.pcb.matrix_layout --route

pcb-matrix-route: pcb-matrix

pcb-matrix-reroute: schematic-matrix
	/usr/bin/python3 -m hardware.pcb.matrix_layout --reroute

pcb-matrix-drc: pcb-matrix
	$(KICAD_CLI) pcb drc --exit-code-violations --schematic-parity --output hardware/pcb/generated/matrix/matrix-drc.rpt hardware/pcb/generated/matrix/matrix.kicad_pcb

pcb-matrix-fab: schematic-matrix
	$(PYTHON) -m hardware.pcb.fab matrix

pcb-hub: schematic-hub
	/usr/bin/python3 -m hardware.pcb.hub_layout --route

pcb-hub-route: pcb-hub

pcb-hub-reroute: schematic-hub
	/usr/bin/python3 -m hardware.pcb.hub_layout --reroute

pcb-hub-drc: pcb-hub
	$(KICAD_CLI) pcb drc --exit-code-violations --schematic-parity --output hardware/pcb/generated/hub/hub-drc.rpt hardware/pcb/generated/hub/hub.kicad_pcb

pcb-hub-fab: schematic-hub
	$(PYTHON) -m hardware.pcb.fab hub

pcb-power: schematic-power
	/usr/bin/python3 -m hardware.pcb.power_layout --route

pcb-power-reroute: schematic-power
	/usr/bin/python3 -m hardware.pcb.power_layout --reroute

pcb-power-drc: pcb-power
	$(KICAD_CLI) pcb drc --exit-code-violations --schematic-parity --output hardware/pcb/generated/power/power-drc.rpt hardware/pcb/generated/power/power.kicad_pcb

pcb-power-fab: schematic-power
	$(PYTHON) -m hardware.pcb.fab power

power-rail-fit:
	$(PYTHON) -m hardware.cad.power_rail_fit

# One fabricated panel holding both light bars and the power board, snapped
# apart after delivery. Built from the routed boards, so re-run it after any
# of them changes.
panel: pcb-lightbar pcb-power
	/usr/bin/python3 -m hardware.pcb.panel

# Layout runs under the system interpreter: pcbnew ships with the native
# KiCad install and is not importable from the venv.
pcb-lightbar: schematic-lightbar
	/usr/bin/python3 -m hardware.pcb.lightbar_layout

pcb-lightbar-drc: pcb-lightbar
	$(KICAD_CLI) pcb drc --exit-code-violations --schematic-parity --output hardware/pcb/generated/lightbar/lightbar-drc.rpt hardware/pcb/generated/lightbar/lightbar.kicad_pcb

pcb-lightbar-fab: schematic-lightbar
	$(PYTHON) -m hardware.pcb.fab lightbar

pcb-fab: pcb-lightbar-fab pcb-matrix-fab pcb-hub-fab

clean:
	rm -rf hardware/pcb/generated hardware/sim/generated hardware/cad/generated \
		software/firmware/build software/firmware/target/build
