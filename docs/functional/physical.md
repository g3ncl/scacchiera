# Physical form and read budget

The fixed geometry of the board, the continuous playing surface, and the tag-to-surface distance the
sensing has to read through. These are product requirements: the sensing implementation is designed
to meet them, not the other way around. Nothing here names an antenna count, a quadrant, or a PCB
topology; those belong to the implementation docs.

## Fixed geometry

| Item | Dimension |
| --- | ---: |
| Square pitch | 35.0 mm |
| Play area | 280 x 280 mm (8 x 8 squares) |
| Side rails | 15 mm |
| Player rails | 50 mm |
| Overall board | 310 x 380 mm |
| Body height before feet | 32 mm target |

Square centers are on a 35 mm grid across the 280 x 280 mm play area. The two player rails are wider
than the side rails because they carry the displays, the light bars, and the service volume for the
hub and battery.

## Continuous top surface

No contact, pad, sensor, or hole is visible within a square. The structural face is one continuous
280 x 280 mm sheet (1.0 mm G10 or FR4) with light and dark real-wood veneer squares bonded to it
through a thin, controlled adhesive layer. The target carrier plus adhesive plus veneer thickness is
1.75 mm or less, and it must be uniform because the read margin depends on distance. There are no
holes through this stack inside the play area.

The face is supported along the 35 mm grid lines and the perimeter; the sensing PCB mounts
independently and carries no top-surface load.

## Read budget

The complete distance from a resting piece's tag to the sensing plane is no greater than 3.0 mm.
This is the budget the sensing architecture is designed against, and the reason a lower-Q, imperfect
antenna still reads a piece on the surface while rejecting one off the board.

From top to bottom the resting stack is:

1. piece body;
2. thin felt over a centered NFC tag recess;
3. sealed wood veneer;
4. adhesive;
5. G10 carrier;
6. a small controlled air gap;
7. the sensing PCB.

Keep conductive objects at least 10 mm behind the sensing plane until an assembled RF check proves a
smaller distance. Route metal inserts, the battery, display shields, and the hub under the outer
rails where possible.

## Pieces

Each piece carries a hidden NFC tag in a centered 22 mm recess and uses nonconductive ballast only. A
steel washer or any metal immediately above the tag is prohibited; if an existing piece contains
metal, remove it or redesign the base rather than adding an anti-metal tag with different RF
behavior. The tag identifies the piece (see [gameplay.md](gameplay.md) for provisioning and the piece
record); the tag type and the reader are an implementation choice, not fixed here.

Every base is at least 24 mm across, pawns included. This overrides conventional chess proportions
deliberately. At the 35 mm grid a conventional pawn base is about 20.5 mm (0.586 of the square),
smaller than the recess it has to contain, and the smaller tags that would fit such a base cost
three to five times as much, are sold as sealed pucks or anti-metal discs rather than thin inlays,
and couple far more weakly because coupling scales with coil area. Buying the tag margin is worth
more here than matching a traditional silhouette. The visible cost is that pawn bases end up close
to the king's, so the set reads as more uniform at the base than a classic Staunton.
