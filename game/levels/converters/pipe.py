"""Pipe compound converter."""

from typing import Dict, Optional, Tuple

from ...content.tile_definitions import require_tile
from ..types import Compound, ParserContext

TilePlacement = Dict[Tuple[int, int], str]

PIPE_LEFT = require_tile("pipe_left")
PIPE_RIGHT = require_tile("pipe_right")
PIPE_MOUTH_LEFT = require_tile("pipe_mouth_left")
PIPE_MOUTH_RIGHT = require_tile("pipe_mouth_right")


def convert_pipe(compound: Compound, context: ParserContext) -> Optional[TilePlacement]:
    """Convert a pipe compound to tile placements.

    Pipes must be exactly 2 characters wide and form a solid rectangle.

    Args:
        compound: Pipe compound to convert
        context: Parser context

    Returns:
        Dictionary mapping positions to tile IDs, or None if invalid shape
    """
    # Validate: pipes must be exactly 2 wide
    if compound.width != 2:
        context.add_error(
            f"Pipe at ({compound.origin_x}, {compound.origin_y}) "
            f"must be exactly 2 characters wide, got {compound.width}"
        )
        return None

    # Validate: must be solid (no gaps)
    if not compound.is_solid:
        context.add_error(
            f"Pipe at ({compound.origin_x}, {compound.origin_y}) has gaps - "
            "must be solid rectangle"
        )
        return None

    # Valid pipe - generate tiles
    tiles: TilePlacement = {}
    for y in range(compound.height):
        if compound.is_top(y):
            # Mouth tiles at the top
            tiles[compound.to_world(0, y)] = PIPE_MOUTH_LEFT
            tiles[compound.to_world(1, y)] = PIPE_MOUTH_RIGHT
        else:
            # Body tiles
            tiles[compound.to_world(0, y)] = PIPE_LEFT
            tiles[compound.to_world(1, y)] = PIPE_RIGHT

    return tiles
