"""Coupling of the sixteen line antennas once they are on sixteen strips.

The split moves the two antenna planes off one substrate's two faces and onto
two stacked substrates. Every x and y stays where it was, so the only thing that
can change is what the plane separation does to the coupling, and that is the
one number the whole partition has to be judged on.

It runs through `antenna_coupling`'s solver and `antenna_coupling`'s loop path,
with nothing but the plane height substituted. Two extractions from one model is
what makes the comparison a comparison rather than two independent claims.

The monolith separates its planes by one 1.0 mm substrate less both claddings,
0.965 mm. The strips separate theirs by one 0.6 mm substrate plus the frame's
0.4 mm rib plus one cladding, 1.035 mm, so the split ends up 7 percent further
apart and couples slightly less. That is a consequence of the stackup rather
than a target: `INTERPLANE_GAP` was chosen to reproduce the monolith, because a
split that changed the coupling would have invalidated every figure in
criteria.yaml at the same time as changing the board.
"""

from hardware.pcb.matrix_geometry import ROW_COUNT
from hardware.pcb.strip_geometry import INTERPLANE_GAP, STRIP_THICKNESS
from hardware.sim.antenna_coupling import COPPER_THICKNESS_MM, Coupling, deck, solve


# Rows are the lower plane, their loop on the strip's top copper, sitting on the
# frame floor. Columns are the upper plane, the same board on ribs above, so the
# column loop faces the pieces exactly as the monolith's front-copper rows did.
ROW_PLANE_Z_MM = 0.0
COLUMN_PLANE_Z_MM = COPPER_THICKNESS_MM + INTERPLANE_GAP + STRIP_THICKNESS


def plane_z(line: int) -> float:
    return ROW_PLANE_Z_MM if line < ROW_COUNT else COLUMN_PLANE_Z_MM


def plane_separation_mm() -> float:
    return COLUMN_PLANE_Z_MM - ROW_PLANE_Z_MM


def strip_deck() -> str:
    return deck(
        plane_z,
        title=(
            f"two stacked {STRIP_THICKNESS} mm strips, planes "
            f"{plane_separation_mm():.3f} mm apart"
        ),
    )


def extract() -> Coupling:
    return solve(strip_deck(), name="strip_stack")


if __name__ == "__main__":
    coupling = extract()
    print(f"plane separation {plane_separation_mm():.3f} mm")
    print(f"self inductance {coupling.inductance_h[0] * 1e9:.1f} nH")
    adjacent = max(
        coupling.coupling_coefficient(i, i + 1)
        for i in (0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14)
    )
    crossing = max(
        coupling.coupling_coefficient(row, column)
        for row in range(ROW_COUNT)
        for column in range(ROW_COUNT, 2 * ROW_COUNT)
    )
    print(f"worst adjacent-line coupling {adjacent:.4f}")
    print(f"worst row-to-column coupling {crossing:.4f}")
