"""Give SKiDL the KiCad library paths outside of `make`.

`make check` exports KICAD9_SYMBOL_DIR and KICAD_FOOTPRINT_DIR before running
pytest, but a bare `pytest` invocation does not inherit them. Without
KICAD9_SYMBOL_DIR, SKiDL cannot open its built-in connector symbols and any
test that builds a circuit errors instead of running. Set the same defaults
the Makefile uses, here, so plain `pytest` matches `make check`.
"""

import os
from pathlib import Path


_FLATPAK_RUNTIME = Path.home() / ".local" / "share" / "flatpak" / "runtime"
_DEFAULT_SYMBOL_DIR = (
    _FLATPAK_RUNTIME / "org.kicad.KiCad.Library.Symbols" / "x86_64" / "stable" / "active" / "files" / "symbols"
)
_DEFAULT_FOOTPRINT_DIR = (
    _FLATPAK_RUNTIME / "org.kicad.KiCad.Library.Footprints" / "x86_64" / "stable" / "active" / "files" / "footprints"
)

# setdefault leaves an explicit user setting untouched and only fills the gap.
os.environ.setdefault("KICAD9_SYMBOL_DIR", str(_DEFAULT_SYMBOL_DIR))
os.environ.setdefault("KICAD_FOOTPRINT_DIR", str(_DEFAULT_FOOTPRINT_DIR))
