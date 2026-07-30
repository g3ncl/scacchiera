"""Conservative service-volume allocation for the power subsystem.

This is not a battery-pack model. The protected assembly is not bound, so the
larger rectangular allocation remains the mechanical acceptance boundary a
supplier drawing has to fit. The cylindrical reference is the maximum listed
body of the leading protected-pack candidate. Leads and their bend stay open.
"""

from dataclasses import dataclass
from pathlib import Path

from build123d import Align, Axis, Box, Compound, Cylinder, Location, Part, export_step


RAIL_LENGTH_MM = 310.0
RAIL_WIDTH_MM = 46.0
RAIL_HEIGHT_MM = 24.0

PACK_LENGTH_MM = 80.0
PACK_WIDTH_MM = 26.0
PACK_HEIGHT_MM = 23.0
CELL_LENGTH_MM = 75.45
CELL_DIAMETER_MM = 22.25

POWER_BOARD_LENGTH_MM = 90.0
POWER_BOARD_WIDTH_MM = 32.0
POWER_BOARD_HEIGHT_MM = 10.0

END_CLEARANCE_MM = 5.0
ASSEMBLY_GAP_MM = 5.0


@dataclass(frozen=True)
class Allocation:
    """Axis-aligned service allocation measured from the rail cavity origin."""

    name: str
    x_mm: float
    y_mm: float
    z_mm: float
    length_mm: float
    width_mm: float
    height_mm: float

    @property
    def x_end_mm(self) -> float:
        return self.x_mm + self.length_mm

    @property
    def y_end_mm(self) -> float:
        return self.y_mm + self.width_mm

    @property
    def z_end_mm(self) -> float:
        return self.z_mm + self.height_mm


@dataclass(frozen=True)
class PowerRailFit:
    pack: Allocation
    board: Allocation

    @property
    def remaining_length_mm(self) -> float:
        return RAIL_LENGTH_MM - self.board.x_end_mm - END_CLEARANCE_MM


def fit() -> PowerRailFit:
    """Place the provisional pack and routed board sequentially in one rail."""
    pack = Allocation(
        "protected-cell allocation",
        END_CLEARANCE_MM,
        (RAIL_WIDTH_MM - PACK_WIDTH_MM) / 2.0,
        0.0,
        PACK_LENGTH_MM,
        PACK_WIDTH_MM,
        PACK_HEIGHT_MM,
    )
    board = Allocation(
        "power-board allocation",
        pack.x_end_mm + ASSEMBLY_GAP_MM,
        (RAIL_WIDTH_MM - POWER_BOARD_WIDTH_MM) / 2.0,
        0.0,
        POWER_BOARD_LENGTH_MM,
        POWER_BOARD_WIDTH_MM,
        POWER_BOARD_HEIGHT_MM,
    )
    return PowerRailFit(pack=pack, board=board)


def _box(allocation: Allocation) -> Part:
    shape = Box(
        allocation.length_mm,
        allocation.width_mm,
        allocation.height_mm,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )
    return shape.moved(Location((allocation.x_mm, allocation.y_mm, allocation.z_mm)))


def model() -> Compound:
    """Build both allocations and the candidate protected-body reference."""
    allocation = fit()
    pack = _box(allocation.pack)
    board = _box(allocation.board)
    cell = Cylinder(CELL_DIAMETER_MM / 2.0, CELL_LENGTH_MM).rotate(
        Axis.Y, -90.0
    ).moved(
        Location(
            (
                allocation.pack.x_mm + PACK_LENGTH_MM / 2.0,
                RAIL_WIDTH_MM / 2.0,
                PACK_HEIGHT_MM / 2.0,
            )
        )
    )
    return Compound(children=(pack, board, cell))


def export(path: Path) -> Path:
    """Export the service allocations and cell reference as STEP."""
    path.parent.mkdir(parents=True, exist_ok=True)
    export_step(model(), path)
    return path


if __name__ == "__main__":
    destination = Path(__file__).parent / "generated" / "power-rail-fit.step"
    result = fit()
    export(destination)
    print(f"STEP: {destination}")
    print(f"unused rail length: {result.remaining_length_mm:.1f} mm")
