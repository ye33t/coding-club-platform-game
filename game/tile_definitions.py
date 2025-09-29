"""Tile definitions mapping tile IDs to properties."""

from typing import Optional, TypedDict

from .collision_shapes import CollisionType


class TileDefinition(TypedDict):
    """Definition for a tile type."""

    sprite_sheet: str  # Which sprite sheet to use
    sprite_name: Optional[str]  # Name of sprite in the sheet (None for empty tiles)
    collision_type: CollisionType  # Collision behavior


# Tile type constants (matching level.py)
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_BRICK = 2
TILE_PIPE = 3
TILE_SLOPE_UP = 4
TILE_SLOPE_DOWN = 5

# Tile definitions registry
TILE_DEFS: dict[int, TileDefinition] = {
    TILE_EMPTY: {
        "sprite_sheet": "background",
        "sprite_name": None,  # No sprite for empty tiles
        "collision_type": CollisionType.EMPTY,
    },
    TILE_GROUND: {
        "sprite_sheet": "background",
        "sprite_name": "ground",
        "collision_type": CollisionType.SOLID,
    },
    TILE_BRICK: {
        "sprite_sheet": "background",
        "sprite_name": "brick",
        "collision_type": CollisionType.SOLID,
    },
    TILE_PIPE: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_left",  # Placeholder
        "collision_type": CollisionType.SOLID,
    },
    TILE_SLOPE_UP: {
        "sprite_sheet": "background",
        "sprite_name": "mound_left_45",
        "collision_type": CollisionType.SLOPE_UP,
    },
    TILE_SLOPE_DOWN: {
        "sprite_sheet": "background",
        "sprite_name": "mound_right_45",
        "collision_type": CollisionType.SLOPE_DOWN,
    },
}


def get_tile_definition(tile_type: int) -> Optional[TileDefinition]:
    """Get the definition for a tile type.

    Args:
        tile_type: The tile type ID

    Returns:
        TileDefinition for this tile, or None if not found
    """
    return TILE_DEFS.get(tile_type)