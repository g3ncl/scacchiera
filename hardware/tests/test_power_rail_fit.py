"""Mechanical allocation checks for the protected cell and power board."""

from hardware.cad.power_rail_fit import (
    ASSEMBLY_GAP_MM,
    CELL_DIAMETER_MM,
    CELL_LENGTH_MM,
    END_CLEARANCE_MM,
    PACK_HEIGHT_MM,
    PACK_LENGTH_MM,
    PACK_WIDTH_MM,
    RAIL_HEIGHT_MM,
    RAIL_LENGTH_MM,
    RAIL_WIDTH_MM,
    fit,
    model,
)


def test_candidate_cell_fits_inside_the_protected_pack_allocation() -> None:
    assert CELL_LENGTH_MM < PACK_LENGTH_MM
    assert CELL_DIAMETER_MM < PACK_WIDTH_MM
    assert CELL_DIAMETER_MM < PACK_HEIGHT_MM


def test_power_allocations_fit_inside_the_player_rail() -> None:
    result = fit()
    for allocation in (result.pack, result.board):
        assert allocation.x_mm >= END_CLEARANCE_MM
        assert allocation.x_end_mm <= RAIL_LENGTH_MM - END_CLEARANCE_MM
        assert allocation.y_mm >= 0.0
        assert allocation.y_end_mm <= RAIL_WIDTH_MM
        assert allocation.z_mm >= 0.0
        assert allocation.z_end_mm <= RAIL_HEIGHT_MM


def test_pack_and_board_have_a_deliberate_harness_gap() -> None:
    result = fit()
    assert result.board.x_mm - result.pack.x_end_mm == ASSEMBLY_GAP_MM
    assert result.remaining_length_mm == 125.0


def test_step_model_keeps_allocations_and_cell_as_separate_solids() -> None:
    solids = model().solids()
    assert len(solids) == 3
    for solid in solids:
        bounds = solid.bounding_box()
        assert bounds.min.X >= 0.0
        assert bounds.max.X <= RAIL_LENGTH_MM
        assert bounds.min.Y >= 0.0
        assert bounds.max.Y <= RAIL_WIDTH_MM
        assert bounds.min.Z >= 0.0
        assert bounds.max.Z <= RAIL_HEIGHT_MM
