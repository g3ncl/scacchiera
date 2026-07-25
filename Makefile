PYTHON := .venv/bin/python
XDG_DATA_HOME := $(CURDIR)/.cache/data
XDG_CACHE_HOME := $(CURDIR)/.cache/cache
XDG_CONFIG_HOME := $(CURDIR)/.cache/config
MPLCONFIGDIR := $(CURDIR)/.cache/matplotlib
KICAD9_SYMBOL_DIR := $(HOME)/.local/share/flatpak/runtime/org.kicad.KiCad.Library.Symbols/x86_64/stable/active/files/symbols
KICAD_FOOTPRINT_DIR := $(HOME)/.local/share/flatpak/runtime/org.kicad.KiCad.Library.Footprints/x86_64/stable/active/files/footprints
KICAD_CLI := /usr/bin/kicad-cli

export XDG_DATA_HOME
export XDG_CACHE_HOME
export XDG_CONFIG_HOME
export MPLCONFIGDIR
export KICAD9_SYMBOL_DIR
export KICAD_FOOTPRINT_DIR

.PHONY: check footprints schematic-lightbar schematic-matrix schematic-hub \
	pcb-lightbar pcb-lightbar-drc pcb-lightbar-fab \
	pcb-matrix pcb-matrix-route pcb-matrix-drc pcb-matrix-fab \
	pcb-hub pcb-hub-route pcb-hub-drc pcb-hub-fab pcb-fab clean

check: schematic-lightbar schematic-matrix schematic-hub pcb-lightbar-drc
	$(PYTHON) -m mypy hardware
	$(PYTHON) -m pytest

# The matrix and hub DRC targets need their routed boards; routing is the
# manual multi-minute pcb-*-route step, so they stay out of `check`.

schematic-lightbar: footprints
	$(PYTHON) -m hardware.pcb.generate lightbar

schematic-matrix: footprints
	$(PYTHON) -m hardware.pcb.generate matrix

schematic-hub: footprints
	$(PYTHON) -m hardware.pcb.generate hub

footprints:
	$(PYTHON) -m hardware.pcb.footprints

# Placement is deterministic; --route runs Freerouting (needs java and the
# jar, several minutes) and imports the result back.
pcb-matrix: schematic-matrix
	/usr/bin/python3 -m hardware.pcb.matrix_layout

pcb-matrix-route: schematic-matrix
	/usr/bin/python3 -m hardware.pcb.matrix_layout --route

pcb-matrix-drc:
	$(KICAD_CLI) pcb drc --exit-code-violations --output hardware/pcb/generated/matrix/matrix-drc.rpt hardware/pcb/generated/matrix/matrix.kicad_pcb

pcb-matrix-fab: schematic-matrix
	$(PYTHON) -m hardware.pcb.fab matrix

pcb-hub: schematic-hub
	/usr/bin/python3 -m hardware.pcb.hub_layout

pcb-hub-route: schematic-hub
	/usr/bin/python3 -m hardware.pcb.hub_layout --route

pcb-hub-drc:
	$(KICAD_CLI) pcb drc --exit-code-violations --output hardware/pcb/generated/hub/hub-drc.rpt hardware/pcb/generated/hub/hub.kicad_pcb

pcb-hub-fab: schematic-hub
	$(PYTHON) -m hardware.pcb.fab hub

# Layout runs under the system interpreter: pcbnew ships with the native
# KiCad install and is not importable from the venv.
pcb-lightbar: schematic-lightbar
	/usr/bin/python3 -m hardware.pcb.lightbar_layout

pcb-lightbar-drc: pcb-lightbar
	$(KICAD_CLI) pcb drc --exit-code-violations --output hardware/pcb/generated/lightbar/lightbar-drc.rpt hardware/pcb/generated/lightbar/lightbar.kicad_pcb

pcb-lightbar-fab: schematic-lightbar
	$(PYTHON) -m hardware.pcb.fab lightbar

pcb-fab: pcb-lightbar-fab pcb-matrix-fab pcb-hub-fab

clean:
	rm -rf hardware/pcb/generated hardware/sim/generated hardware/cad/generated
