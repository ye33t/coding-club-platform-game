"""Background cloud compound converter."""

from typing import Dict, Optional, Tuple

from ...content.tile_definitions import require_tile
from ..types import Compound, ParserContext

TilePlacement = Dict[Tuple[int, int], str]

CLOUD_TOP_LEFT = require_tile("cloud_top_left")
CLOUD_TOP = require_tile("cloud_top")
CLOUD_TOP_RIGHT = require_tile("cloud_top_right")
CLOUD_BOTTOM_LEFT = require_tile("cloud_bottom_left")
CLOUD_BOTTOM = require_tile("cloud_bottom")
CLOUD_BOTTOM_RIGHT = require_tile("cloud_bottom_right")


def convert_cloud(
    compound: Compound, context: ParserContext
) -> Optional[TilePlacement]:
    """Convert a cloud compound into tile placements.

    Clouds are rendered as Nx2 rectangles (N >= 3) with no gaps.

    Args:
        compound: Cloud compound to convert
        context: Parser context

    Returns:
        Dictionary mapping positions to tile IDs, or None if invalid shape
    """
    min_width = 3
    expected_height = 2

    if compound.height != expected_height:
        context.add_error(
            (
                f"Cloud at ({compound.origin_x}, {compound.origin_y}) must be "
                f"{expected_height} tiles tall, got {compound.height}"
            )
        )
        return None

    if compound.width < min_width:
        context.add_error(
            (
                f"Cloud at ({compound.origin_x}, {compound.origin_y}) must be at "
                f"least {min_width} tiles wide, got {compound.width}"
            )
        )
        return None

    if not compound.is_solid:
        context.add_error(
            f"Cloud at ({compound.origin_x}, {compound.origin_y}) must be solid"
        )
        return None

    tiles: TilePlacement = {}
    for local_y in range(expected_height):
        for local_x in range(compound.width):
            world_pos = compound.to_world(local_x, local_y)
            if local_y == expected_height - 1:
                # Top row
                if local_x == 0:
                    tiles[world_pos] = CLOUD_TOP_LEFT
                elif local_x == compound.width - 1:
                    tiles[world_pos] = CLOUD_TOP_RIGHT
                else:
                    tiles[world_pos] = CLOUD_TOP
            else:
                # Bottom row
                if local_x == 0:
                    tiles[world_pos] = CLOUD_BOTTOM_LEFT
                elif local_x == compound.width - 1:
                    tiles[world_pos] = CLOUD_BOTTOM_RIGHT
                else:
                    tiles[world_pos] = CLOUD_BOTTOM

    return tiles
