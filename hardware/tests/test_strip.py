"""The split sensing plane's schematics and geometry.

Sixteen strips and two spines have to add up to exactly what the monolithic
matrix board is, or the split has quietly changed the circuit as well as the
partition. These tests hold that equivalence: same cells, same registers, same
one-hot selection, same loop copper in the same place.
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
    ROW_COUNT,
    SQUARE_PITCH,
    line_center,
)
from hardware.pcb.spine import build_spine
from hardware.pcb.strip import build_strip
from hardware.pcb.strip_geometry import (
    LOOP_CENTER_ACROSS,
    PLANE_SEPARATION,
    SPINE_LENGTH,
    SPINE_SOCKETS,
    SPINE_WIDTH,
    STRIP_LENGTH,
    STRIP_WIDTH,
    socket_reference,
    spine_socket_x,
    strip_component_slots,
)


CRITERIA = yaml.safe_load(
    (Path(__file__).parent.parent.parent / "docs" / "hardware" / "criteria.yaml").read_text()
)["criteria"]


def _limit(name: str, bound: str) -> float:
    return float(CRITERIA[name]["limits"][bound])


@pytest.fixture(scope="module")
def strip() -> Circuit:
    return build_strip()


@pytest.fixture(scope="module")
def spine() -> Circuit:
    return build_spine()


def _references(circuit: Circuit) -> set[str]:
    return {str(part.ref) for part in circuit.parts}


def _net_names(circuit: Circuit) -> set[str]:
    return {str(net.name) for net in circuit.nets}


def test_a_strip_carries_exactly_one_switch_cell(strip: Circuit) -> None:
    """Thirteen cell parts and nothing else that switches.

    The strip is the matrix board's cell lifted onto its own substrate. If a
    part appears here that the cell does not have, the split has grown a circuit
    rather than moved one.
    """
    cell_parts = {
        "C1", "C2", "C3", "C4", "D1", "D2", "L1", "L2", "Q1", "Q2", "R1", "R2", "R3",
    }
    assert _references(strip) == cell_parts | {"J1", "#FLG01", "#FLG02"}


def test_the_tank_never_crosses_the_connector(strip: Circuit) -> None:
    """The nets that set the resonance must all be local to the strip.

    This is the whole reason the partition is buildable. An earlier proposal put
    the board boundary between the loop and its tuning capacitor, which would
    have placed connector inductance inside sixteen resonators; here the
    connector sits on the far side of the 100 nF DC block, so it loads the
    shared bus instead. Anything on the connector that also touches the tank
    would undo that.
    """
    tank_nets = {"LINE0_MATCH", "LINE0_COIL", "LINE0_BUS", "LINE0_INJECT"}
    connector = next(part for part in strip.parts if str(part.ref) == "J1")
    connector_nets = {
        str(pin.net.name) for pin in connector.pins if pin.net is not None
    }
    assert not tank_nets & connector_nets
    assert connector_nets == {"GND", "RF_BUS", "3V3", "SEL_N"}


def test_the_loop_sits_where_the_monolith_puts_it(strip: Circuit) -> None:
    """Same footprint, so the extracted and simulated copper is unchanged."""
    antenna = next(part for part in strip.parts if str(part.ref) == "L2")
    assert antenna.footprint == "Chessboard:Antenna_Line"
    assert STRIP_LENGTH == BOARD_SIZE


def test_the_strip_fits_its_lane_with_a_rib_to_spare() -> None:
    """The loop has to clear the board edge and the strips have to clear each
    other, or the printed frame has nothing to hold them apart with."""
    loop_edge_clearance = (STRIP_WIDTH - LOOP_BREADTH) / 2.0
    assert loop_edge_clearance >= 0.2, "loop copper is inside the edge rule"
    assert SQUARE_PITCH - STRIP_WIDTH >= 1.0, "no room for a frame rib between strips"
    assert LOOP_CENTER_ACROSS == STRIP_WIDTH / 2.0


def test_every_cell_part_has_a_slot_and_the_slots_are_inside_the_zone() -> None:
    slots = strip_component_slots()
    assert len(slots) == 12
    for reference, (x, y) in slots.items():
        assert 0.0 < x < 14.5, f"{reference} at x={x} is past the pour edge"
        assert 0.0 < y < STRIP_WIDTH, f"{reference} at y={y} is off the strip"


def test_two_spines_hold_the_matrix_board_s_two_registers(spine: Circuit) -> None:
    """One 74HC595 per spine, eight sockets, and the chain in and out.

    Two of these are the monolith's U1 and U2, and the pair has to chain the
    same way or the sixteen-bit shift the firmware already does stops landing
    one-hot.
    """
    assert _references(spine) == (
        {"U1", "C1", "J1", "J2", "H1", "H2", "#FLG01", "#FLG02"}
        | {socket_reference(index) for index in range(SPINE_SOCKETS)}
    )
    assert "SEL_CHAIN" in _net_names(spine)
    register = next(part for part in spine.parts if str(part.ref) == "U1")
    outputs = {
        str(pin.net.name)
        for pin in register.pins
        if pin.net is not None and str(pin.net.name).startswith("SEL") and "_N" in str(pin.net.name)
    }
    assert outputs == {f"SEL{index}_N" for index in range(SPINE_SOCKETS)}


def test_the_split_selects_the_same_sixteen_lines_as_the_monolith(spine: Circuit) -> None:
    """Two spines of eight is sixteen one-hot selections, as before."""
    assert SPINE_SOCKETS * 2 == LINE_COUNT


def test_the_socket_pitch_tracks_the_lane_pitch() -> None:
    """Socket i has to land under strip i, or no harness reaches its own board."""
    for index in range(SPINE_SOCKETS - 1):
        step = spine_socket_x(index + 1) - spine_socket_x(index)
        assert step == pytest.approx(SQUARE_PITCH)
    span = spine_socket_x(SPINE_SOCKETS - 1) - spine_socket_x(0)
    assert span == pytest.approx(SQUARE_PITCH * (ROW_COUNT - 1))
    assert spine_socket_x(0) > 0.0
    assert spine_socket_x(SPINE_SOCKETS - 1) < SPINE_LENGTH


def test_the_split_introduces_no_new_component_type(strip: Circuit, spine: Circuit) -> None:
    """Every part number on both boards already appears on the matrix board.

    A new unique Extended part costs a 2.70 EUR feeder change and a datasheet
    ingest, and the split needs neither: the strip's connector is the same
    SM07B-GHS-TB the matrix board binds, seven conductors and all.
    """
    def fitted_mpns(circuit: Circuit) -> set[str]:
        return {
            str(part.manf_num)
            for part in circuit.parts
            if getattr(part, "fitted", "") == "yes" and str(part.manf_num)
        }

    monolith = fitted_mpns(build_matrix())
    assert fitted_mpns(strip) - monolith == set()
    assert fitted_mpns(spine) - monolith == set()


def test_the_two_planes_sit_where_the_monolith_s_two_faces_did() -> None:
    minimum = _limit("STRIP-PLANE-SEPARATION", "minimum")
    maximum = _limit("STRIP-PLANE-SEPARATION", "maximum")
    assert minimum <= PLANE_SEPARATION + 0.035 <= maximum


def test_the_substrate_the_split_costs_is_bounded() -> None:
    """TEST-STRIP-COST-001.

    The monolith carries two antenna planes on one substrate's two faces. Any
    per-line strip uses one face and wastes the other, so the split buys roughly
    twice the area no matter how it is drawn. Recorded as a ceiling so widening
    a strip or a spine cannot quietly make the trade worse.
    """
    split = LINE_COUNT * STRIP_LENGTH * STRIP_WIDTH + 2 * SPINE_LENGTH * SPINE_WIDTH
    monolith = BOARD_SIZE * BOARD_SIZE
    assert split / monolith <= _limit("STRIP-PANEL-AREA-RATIO", "maximum")


def test_the_strip_has_no_mounting_hole(strip: Circuit) -> None:
    """Deliberate, and the frame channel is why. Asserted so that adding one
    back is a decision rather than a drift: there is nowhere on a strip a
    grounded pad can go without either sitting in the cell zone or loading the
    loop from 3.2 mm away."""
    assert not any(str(part.ref).startswith("H") for part in strip.parts)


def test_line_centres_are_unchanged_by_the_split() -> None:
    """The play-area registration is the one thing the split must not move."""
    for index in range(ROW_COUNT):
        assert line_center(index) == pytest.approx(
            spine_socket_x(index) + (line_center(0) - spine_socket_x(0))
        )
