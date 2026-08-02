"""The split sensing plane's schematic and geometry.

Four boards have to add up to exactly what the monolithic matrix board is, or
the split has quietly changed the circuit as well as the partition. These tests
hold that equivalence: same cells, same register part, same one-hot selection,
same loop copper in the same place.
"""

from pathlib import Path

import pytest
import yaml
from skidl import Circuit

from hardware.pcb.matrix import build_matrix
from hardware.pcb.matrix_geometry import (
    BOARD_SIZE,
    LINE_COUNT,
    LOOP_BREADTH,
    PLAY_ORIGIN,
    PLAY_SPAN,
    SQUARE_PITCH,
)
from hardware.pcb.quad import REGISTER_OUTPUTS, build_quad
from hardware.pcb.quad_geometry import (
    BOARD_COUNT,
    LANES_PER_BOARD,
    PLANE_SEPARATION,
    POUR_EDGE,
    QUAD_LENGTH,
    QUAD_WIDTH,
    antenna_reference,
    cell_slots,
    lane_center,
)


CRITERIA = yaml.safe_load(
    (Path(__file__).parent.parent.parent / "docs" / "hardware" / "criteria.yaml").read_text()
)["criteria"]


def _limit(name: str, bound: str) -> float:
    return float(CRITERIA[name]["limits"][bound])


@pytest.fixture(scope="module")
def quad() -> Circuit:
    return build_quad()


def _references(circuit: Circuit) -> set[str]:
    return {str(part.ref) for part in circuit.parts}


def test_a_board_carries_exactly_four_switch_cells(quad: Circuit) -> None:
    """Forty-eight cell parts and nothing else that switches.

    The board is the matrix board's cell, four times, lifted onto its own
    substrate. A part here that the cell does not have means the split has grown
    a circuit rather than moved one.
    """
    cell_parts = {
        reference
        for lane in range(LANES_PER_BOARD)
        for reference in (*cell_slots(lane), antenna_reference(lane))
    }
    assert len(cell_parts) == LANES_PER_BOARD * 13
    assert _references(quad) == cell_parts | {"J1", "J2", "U1", "C17", "#FLG01", "#FLG02"}


def test_the_tank_never_crosses_a_connector(quad: Circuit) -> None:
    """The nets that set a lane's resonance must all be local to the board.

    This is the whole reason the partition is buildable. An earlier proposal put
    the board boundary between a loop and its tuning capacitor, which would have
    placed connector inductance inside sixteen resonators; here both connectors
    sit on the far side of the 100 nF DC block, so a harness loads the shared bus
    instead. Anything on a link that also touches a tank would undo that.
    """
    tank_nets = {
        f"LINE{lane}_{node}"
        for lane in range(LANES_PER_BOARD)
        for node in ("MATCH", "COIL", "BUS", "INJECT")
    }
    allowed = {
        "GND", "RF_BUS", "3V3", "SEL_SER", "SEL_CHAIN", "SEL_SRCLK", "SEL_RCLK",
    }
    for reference in ("J1", "J2"):
        connector = next(part for part in quad.parts if str(part.ref) == reference)
        carried = {str(pin.net.name) for pin in connector.pins if pin.net is not None}
        assert not tank_nets & carried, f"{reference} reaches a tank node"
        assert carried <= allowed


def test_four_boards_are_the_sixteen_lines(quad: Circuit) -> None:
    assert BOARD_COUNT * LANES_PER_BOARD == LINE_COUNT
    register = next(part for part in quad.parts if str(part.ref) == "U1")
    driven = {
        str(pin.net.name)
        for pin in register.pins
        if pin.net is not None and str(pin.net.name).endswith("_N")
    }
    assert driven == {f"SEL{lane}_N" for lane in range(LANES_PER_BOARD)}
    assert len(REGISTER_OUTPUTS) == LANES_PER_BOARD


def test_the_chain_passes_through_every_board(quad: Circuit) -> None:
    """Serial in on the link in, QH' on the link out, so four boards chain.

    Four eight-bit registers deep is a 32-bit shift where the matrix board is
    16, which is the firmware cost of this partition and is recorded rather than
    discovered at bring-up.
    """
    link_in = next(part for part in quad.parts if str(part.ref) == "J1")
    link_out = next(part for part in quad.parts if str(part.ref) == "J2")
    assert "SEL_SER" in {str(p.net.name) for p in link_in.pins if p.net is not None}
    assert "SEL_CHAIN" in {str(p.net.name) for p in link_out.pins if p.net is not None}


def test_two_boards_tile_a_plane_exactly() -> None:
    """No cumulative pitch error between the two boards of one plane."""
    assert QUAD_WIDTH == SQUARE_PITCH * LANES_PER_BOARD
    assert 2 * QUAD_WIDTH == PLAY_SPAN
    assert QUAD_LENGTH == BOARD_SIZE


def test_the_loops_clear_the_board_edges() -> None:
    loop_edge_clearance = lane_center(0) - LOOP_BREADTH / 2.0
    assert loop_edge_clearance >= 0.2, "loop copper is inside the edge rule"


def test_every_cell_part_has_a_slot_inside_the_component_zone() -> None:
    for lane in range(LANES_PER_BOARD):
        slots = cell_slots(lane)
        assert len(slots) == 12
        for reference, (x, y) in slots.items():
            assert 0.0 < x < POUR_EDGE, f"{reference} at x={x} is past the pour edge"
            assert 0.0 < y < QUAD_WIDTH, f"{reference} at y={y} is off the board"


def test_lane_clusters_leave_room_between_them() -> None:
    """The gaps are where the links and the register go, so they have to exist.

    A rotated GH housing is 11.2 mm across its mounting pads, and this is what
    the 3.6 mm cell row pitch was chosen to protect. At 4.0 mm the gaps closed
    to 11.5 mm and the connector no longer cleared its neighbours.
    """
    for lane in range(LANES_PER_BOARD - 1):
        below = max(y for _, y in cell_slots(lane).values())
        above = min(y for _, y in cell_slots(lane + 1).values())
        assert above - below >= 12.0, f"gap above lane {lane} is {above - below:.1f} mm"


def test_the_split_introduces_no_new_component_type(quad: Circuit) -> None:
    """Every part number already appears on the matrix board.

    A new unique Extended part costs a 2.70 EUR feeder change and a datasheet
    ingest, and the split needs neither: the links are the same SM07B-GHS-TB the
    matrix board binds, seven conductors and all.
    """

    def fitted_mpns(circuit: Circuit) -> set[str]:
        return {
            str(part.manf_num)
            for part in circuit.parts
            if getattr(part, "fitted", "") == "yes" and str(part.manf_num)
        }

    assert fitted_mpns(quad) - fitted_mpns(build_matrix()) == set()


def test_the_two_planes_sit_where_the_monolith_s_two_faces_did() -> None:
    minimum = _limit("QUAD-PLANE-SEPARATION", "minimum")
    maximum = _limit("QUAD-PLANE-SEPARATION", "maximum")
    assert minimum <= PLANE_SEPARATION + 0.035 <= maximum


def test_the_substrate_the_split_costs_is_bounded() -> None:
    """TEST-QUAD-COST-001.

    The monolith carries two antenna planes on one substrate's two faces. Any
    per-lane split uses one face and wastes the other, so it buys roughly twice
    the area no matter how it is drawn. Recorded as a ceiling so widening a
    board cannot quietly make the trade worse.
    """
    split = BOARD_COUNT * QUAD_LENGTH * QUAD_WIDTH
    monolith = BOARD_SIZE * BOARD_SIZE
    assert split / monolith <= _limit("QUAD-PANEL-AREA-RATIO", "maximum")


def test_the_board_has_no_mounting_hole(quad: Circuit) -> None:
    """Deliberate, and the frame channel is why. Asserted so that adding one
    back is a decision rather than a drift: the loops span the board's whole
    width for 276 of its 300 mm, and the connector end is committed."""
    assert not any(str(part.ref).startswith("H") for part in quad.parts)


def test_the_component_zone_is_inside_the_monolith_s_own_margin() -> None:
    """No chin.

    The zone the cells and connectors live in is the 15 mm the play area was
    already offset by, which the matrix board also spends on components, so the
    split adds no protrusion the monolith does not already have.
    """
    assert POUR_EDGE <= PLAY_ORIGIN
    assert QUAD_LENGTH - (PLAY_ORIGIN + PLAY_SPAN) == 5.0
