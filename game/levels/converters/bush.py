"""Background bush compound converter."""

from typing import Dict, Optional, Tuple

from ...tile_definitions import TILE_BUSH_CENTER, TILE_BUSH_LEFT, TILE_BUSH_RIGHT
from ..types import Compound, ParserContext

TilePlacement = Dict[Tuple[int, int], int]


def convert_bush(compound: Compound, context: ParserContext) -> Optional[TilePlacement]:
    """Convert a bush compound into tile placements.

    Bushes are rendered as Nx1 rectangles (N >= 3) with no gaps.

    Args:
        compound: Bush compound to convert
        context: Parser context

    Returns:
        Dictionary mapping positions to tile IDs, or None if invalid shape
    """
    min_width = 3
    expected_height = 1

    if compound.height != expected_height:
        context.add_error(
            (
                f"Bush at ({compound.origin_x}, {compound.origin_y}) must be "
                f"{expected_height} tiles tall, got {compound.height}"
            )
        )
        return None

    if compound.width < min_width:
        context.add_error(
            (
                f"Bush at ({compound.origin_x}, {compound.origin_y}) must be at "
                f"least {min_width} tiles wide, got {compound.width}"
            )
        )
        return None

    if not compound.is_solid:
        context.add_error(
            f"Bush at ({compound.origin_x}, {compound.origin_y}) must be solid"
        )
        return None

    tiles: TilePlacement = {}

    tiles[compound.to_world(0, 0)] = TILE_BUSH_LEFT
    tiles[compound.to_world(compound.width - 1, 0)] = TILE_BUSH_RIGHT

    for local_x in range(1, compound.width - 1):
        tiles[compound.to_world(local_x, 0)] = TILE_BUSH_CENTER

    return tiles
