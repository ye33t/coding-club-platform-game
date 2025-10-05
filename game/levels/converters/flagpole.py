"""Flagpole compound converter."""

from typing import Dict, Optional, Tuple

from ...tile_definitions import TILE_BLOCK, TILE_FLAGPOLE, TILE_FLAGPOLE_TOP
from ..types import Compound, ParserContext

TilePlacement = Dict[Tuple[int, int], int]


def convert_flagpole(
    compound: Compound, context: ParserContext
) -> Optional[TilePlacement]:
    """Convert a flagpole compound to tile placements.

    Flagpoles must be exactly 1 character wide, at least 4 tiles high,
    and form a solid column.

    Args:
        compound: Flagpole compound to convert
        context: Parser context

    Returns:
        Dictionary mapping positions to tile IDs, or None if invalid shape
    """
    # Validate: flagpoles must be exactly 1 wide
    if compound.width != 1:
        context.add_error(
            f"Flagpole at ({compound.origin_x}, {compound.origin_y}) "
            f"must be exactly 1 character wide, got {compound.width}"
        )
        return None

    # Validate: must be solid (no gaps)
    if not compound.is_solid:
        context.add_error(
            f"Flagpole at ({compound.origin_x}, {compound.origin_y}) has gaps - "
            "must be solid column"
        )
        return None

    # Validate: must be at least 4 tiles high
    if compound.height < 4:
        context.add_error(
            f"Flagpole at ({compound.origin_x}, {compound.origin_y}) "
            f"must be at least 4 tiles high, got {compound.height}"
        )
        return None

    # Valid flagpole - generate tiles
    tiles: TilePlacement = {}
    for y in range(compound.height):
        if y == 0:
            # Base block at the bottom
            tiles[compound.to_world(0, y)] = TILE_BLOCK
        elif compound.is_top(y):
            # Flagpole top
            tiles[compound.to_world(0, y)] = TILE_FLAGPOLE_TOP
        else:
            # Middle sections
            tiles[compound.to_world(0, y)] = TILE_FLAGPOLE

    return tiles
