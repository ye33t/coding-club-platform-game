"""Background castle compound converter."""

from typing import Dict, Optional, Tuple

from ...content.tile_definitions import require_tile
from ..types import Compound, ParserContext

TilePlacement = Dict[Tuple[int, int], str]

BATTLEMENT = require_tile("battlement_1")
BRICK = require_tile("brick")
ARCH_LEFT = require_tile("arch_left")
ARCH_CENTER = require_tile("arch_center")
ARCH_RIGHT = require_tile("arch_right")
VOID = require_tile("void")


def convert_castle(
    compound: Compound, context: ParserContext
) -> Optional[TilePlacement]:
    """Convert a castle compound into background tile placements."""
    expected_width = 5
    expected_height = 5

    if compound.width != expected_width or compound.height != expected_height:
        context.add_error(
            (
                f"Castle at ({compound.origin_x}, {compound.origin_y}) must be "
                f"{expected_width}x{expected_height} tiles, got "
                f"{compound.width}x{compound.height}"
            )
        )
        return None

    for local_y in range(expected_height):
        for local_x in range(expected_width):
            filled = compound.mask[local_y][local_x]
            if local_y >= expected_height - 2:
                should_fill = 1 <= local_x <= 3
            else:
                should_fill = True
            if filled != should_fill:
                context.add_error(
                    (
                        "Castle compound must match .KKK./.KKK./KKKKK/KKKKK/KKKKK "
                        f"pattern at ({compound.origin_x}, {compound.origin_y})"
                    )
                )
                return None

    tiles: TilePlacement = {}

    # Top block (rows 3 and 4)
    for local_x in range(1, 4):
        tiles[compound.to_world(local_x, 4)] = BATTLEMENT
    tiles[compound.to_world(1, 3)] = ARCH_LEFT
    tiles[compound.to_world(2, 3)] = BRICK
    tiles[compound.to_world(3, 3)] = ARCH_RIGHT

    # Bottom block (rows 0-2)
    for local_x in range(expected_width):
        tiles[compound.to_world(local_x, 2)] = BATTLEMENT

    for local_x in range(expected_width):
        world_pos = compound.to_world(local_x, 1)
        if local_x == 2:
            tiles[world_pos] = ARCH_CENTER
        else:
            tiles[world_pos] = BRICK

    for local_x in range(expected_width):
        world_pos = compound.to_world(local_x, 0)
        if local_x == 2:
            tiles[world_pos] = VOID
        else:
            tiles[world_pos] = BRICK

    return tiles
