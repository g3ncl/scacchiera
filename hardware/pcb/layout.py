"""Small KiCad board-building helpers shared by the PCB layouts."""

from collections.abc import Iterable
import os
from pathlib import Path

import pcbnew

from hardware.pcb.geometry import Placement, Position
from hardware.pcb.netlist import ComponentRecord, Netlist


__all__ = ["BoardBuilder", "Placement", "Position"]


def _named_field(footprint: pcbnew.FOOTPRINT, name: str) -> pcbnew.PCB_FIELD:
    # The by-name field lookup is GetFieldByName in current pcbnew bindings and
    # an overload of GetField in older ones; the desktop and CI carry different
    # point releases, so both spellings must resolve.
    getter = getattr(footprint, "GetFieldByName", None)
    if getter is not None:
        return getter(name)
    return footprint.GetField(name)


class BoardBuilder:
    """Build a deterministic board from a checked SKiDL netlist."""

    def __init__(self, netlist: Netlist, *, copper_layers: int = 2, board_thickness_mm: float = 1.6) -> None:
        self.board = pcbnew.BOARD()
        self.board.SetCopperLayerCount(copper_layers)
        self.board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(board_thickness_mm))
        self.netlist = netlist
        self.nets = {
            net.name: pcbnew.NETINFO_ITEM(self.board, net.name)
            for net in netlist.nets
        }
        for net in self.nets.values():
            self.board.Add(net)
        self.footprints: dict[str, pcbnew.FOOTPRINT] = {}

    def add_outline(self, width: float, height: float) -> None:
        points = (
            Position(0.0, 0.0),
            Position(width, 0.0),
            Position(width, height),
            Position(0.0, height),
            Position(0.0, 0.0),
        )
        for start, end in zip(points[:-1], points[1:], strict=True):
            segment = pcbnew.PCB_SHAPE(self.board)
            segment.SetShape(pcbnew.SHAPE_T_SEGMENT)
            segment.SetLayer(pcbnew.Edge_Cuts)
            segment.SetWidth(pcbnew.FromMM(0.05))
            segment.SetStart(_vector(start))
            segment.SetEnd(_vector(end))
            self.board.Add(segment)

    def add_component(self, component: ComponentRecord, placement: Placement) -> None:
        library, name = component.footprint.split(":", maxsplit=1)
        footprint = pcbnew.FootprintLoad(str(_library_path(library)), name)
        if footprint is None:
            raise ValueError(f"footprint not found: {component.footprint}")
        footprint.SetReference(component.reference)
        footprint.SetValue(component.value)
        footprint.SetAttributes(footprint.GetAttributes() & ~pcbnew.FP_EXCLUDE_FROM_BOM)
        footprint.SetFPIDAsString(component.footprint)
        _named_field(footprint, "Description").SetText(component.description)
        _named_field(footprint, "Datasheet").SetText(component.datasheet)
        schematic_path = pcbnew.KIID_PATH()
        schematic_path.push_back(pcbnew.KIID(component.schematic_id))
        footprint.SetPath(schematic_path)
        footprint.SetSheetname("/")
        footprint.SetPosition(_vector(placement.position))
        # The reference is the hand-assembly legend; JLCPCB's printable floor
        # is 1 mm text with 0.15 mm strokes. Values stay off the silk: at this
        # density they would be clipped into noise.
        reference = footprint.Reference()
        reference.SetVisible(True)
        reference.SetTextSize(pcbnew.VECTOR2I_MM(1.0, 1.0))
        reference.SetTextThickness(pcbnew.FromMM(0.15))
        footprint.Value().SetVisible(False)
        pad_nets = self.netlist.pad_nets()
        for pad in footprint.Pads():
            net_name = pad_nets.get((component.reference, pad.GetNumber()))
            if net_name is None:
                number = pad.GetNumber()
                if number.isdigit():
                    pin_name = f"Pin_{number}"
                    net_name = f"unconnected-({component.reference}-{pin_name}-Pad{number})"
                    if net_name not in self.nets:
                        self.nets[net_name] = pcbnew.NETINFO_ITEM(self.board, net_name)
                        self.board.Add(self.nets[net_name])
                elif number in {"A6", "A7", "A8", "B6", "B7", "B8"}:
                    pin_name = {
                        "A6": "D+", "B6": "D+", "A7": "D-", "B7": "D-",
                        "A8": "SBU1", "B8": "SBU2",
                    }[number]
                    net_name = f"unconnected-({component.reference}-{pin_name}-Pad{number})"
                    if net_name not in self.nets:
                        self.nets[net_name] = pcbnew.NETINFO_ITEM(self.board, net_name)
                        self.board.Add(self.nets[net_name])
            if net_name is not None:
                pad.SetNet(self.nets[net_name])
        self.board.Add(footprint)
        if placement.back:
            footprint.Flip(_vector(placement.position), False)
        footprint.SetOrientationDegrees(placement.rotation)
        self.footprints[component.reference] = footprint

    def pad_position(self, reference: str, number: str) -> Position:
        positions = self.pad_positions(reference, number)
        if positions:
            return positions[0]
        raise ValueError(f"pad {reference}.{number} not found")

    def pad_positions(self, reference: str, number: str) -> tuple[Position, ...]:
        footprint = self.footprints[reference]
        return tuple(
            Position(pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y))
            for pad in footprint.Pads()
            if pad.GetNumber() == number
        )

    def add_track(
        self,
        net_name: str,
        points: Iterable[Position],
        width: float,
        layer: int = pcbnew.F_Cu,
    ) -> None:
        point_list = tuple(points)
        for start, end in zip(point_list[:-1], point_list[1:], strict=True):
            segment = pcbnew.PCB_TRACK(self.board)
            segment.SetLayer(layer)
            segment.SetWidth(pcbnew.FromMM(width))
            segment.SetNet(self.nets[net_name])
            segment.SetStart(_vector(start))
            segment.SetEnd(_vector(end))
            self.board.Add(segment)

    def add_via(
        self,
        net_name: str,
        position: Position,
        diameter: float = 0.6,
        drill: float = 0.3,
    ) -> None:
        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition(_vector(position))
        via.SetWidth(pcbnew.FromMM(diameter))
        via.SetDrill(pcbnew.FromMM(drill))
        via.SetNet(self.nets[net_name])
        self.board.Add(via)

    def add_mounting_hole(
        self,
        net_name: str,
        position: Position,
        reference: str,
        size: str = "2.7mm_M2.5",
    ) -> None:
        """A plated mounting hole bonded to a net, for screwing the board down.

        Bonding it to ground rather than leaving it isolated ties the enclosure
        screw to the ground pour, so the shell cannot float. KiCad's
        MountingHole footprints carry exclude_from_bom and
        exclude_from_pos_files, which is what keeps a hole out of the JLCPCB
        upload files: it is a hole, not a part to place.
        """
        name = f"MountingHole_{size}_Pad"
        footprint = pcbnew.FootprintLoad(
            str(_library_path("MountingHole")), name
        )
        if footprint is None:
            raise ValueError(f"mounting hole footprint not found: {name}")
        footprint.SetReference(reference)
        footprint.SetPosition(_vector(position))
        footprint.Reference().SetVisible(False)
        footprint.Value().SetVisible(False)
        for pad in footprint.Pads():
            pad.SetNet(self.nets[net_name])
        self.board.Add(footprint)
        self.footprints[reference] = footprint

    def add_zone(self, net_name: str, layer: int, corners: Iterable[Position]) -> None:
        zone = pcbnew.ZONE(self.board)
        zone.SetLayer(layer)
        zone.SetNet(self.nets[net_name])
        zone.SetLocalClearance(pcbnew.FromMM(0.2))
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        outline = zone.Outline()
        outline.NewOutline()
        for corner in corners:
            point = _vector(corner)
            outline.Append(point.x, point.y)
        self.board.Add(zone)

    def add_title(
        self,
        text: str,
        position: Position,
        height: float = 1.3,
        back: bool = False,
    ) -> None:
        """Board identification on the silkscreen, mirrored when it sits on
        the back face so it reads correctly from that side."""
        title = pcbnew.PCB_TEXT(self.board)
        title.SetText(text)
        title.SetLayer(pcbnew.B_SilkS if back else pcbnew.F_SilkS)
        title.SetPosition(_vector(position))
        title.SetTextSize(pcbnew.VECTOR2I_MM(height, height))
        title.SetTextThickness(pcbnew.FromMM(max(0.15, round(height * 0.15, 2))))
        title.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        if back:
            title.SetMirrored(True)
        self.board.Add(title)

    def add_keepout(self, layer: int, corners: Iterable[Position]) -> None:
        """Forbid tracks and vias in a region, leaving the pour there intact.

        On two layers the back copper is both the ground return and the router's
        second routing layer, and a signal crossing it cuts the return path. This
        reserves the areas where that matters instead of accepting whatever the
        router happens to do.
        """
        zone = pcbnew.ZONE(self.board)
        zone.SetLayer(layer)
        zone.SetIsRuleArea(True)
        zone.SetDoNotAllowTracks(True)
        # Vias stay legal: ground stitching between the two pours is wanted here,
        # and a via is only useful to the router if it can leave on a track.
        zone.SetDoNotAllowVias(False)
        # The copper-fill exclusion setter is SetDoNotAllowCopperPour in current
        # pcbnew bindings and SetDoNotAllowZoneFills in older ones.
        setter = getattr(zone, "SetDoNotAllowCopperPour", None)
        if setter is None:
            setter = zone.SetDoNotAllowZoneFills
        setter(False)
        outline = zone.Outline()
        outline.NewOutline()
        for corner in corners:
            point = _vector(corner)
            outline.Append(point.x, point.y)
        self.board.Add(zone)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not pcbnew.SaveBoard(str(path), self.board):
            raise OSError(f"could not save {path}")


def _vector(position: Position) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I_MM(position.x, position.y)


def _library_path(library: str) -> Path:
    if library == "Chessboard":
        return Path(__file__).parent / "generated" / "footprints" / "Chessboard.pretty"
    root = os.environ.get("KICAD_FOOTPRINT_DIR")
    if root is None:
        raise RuntimeError("KICAD_FOOTPRINT_DIR is not set")
    return Path(root) / f"{library}.pretty"
