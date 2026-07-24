"""Placement primitives shared by the layout builder and the layout scripts.

These carry no KiCad dependency, so the pure-geometry placement functions and
their tests can import them without pulling in `pcbnew`, which is only available
under the system interpreter that runs the board generators.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: float
    y: float


@dataclass(frozen=True)
class Placement:
    position: Position
    rotation: float = 0.0
    back: bool = False
