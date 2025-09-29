"""Tile definitions mapping tile IDs to properties.

Collision Masks:
    Each 2x2 tile (16x16 pixels) is divided into 4 quadrants (8x8 pixels each).
    A 4-bit mask represents which quadrants are solid:

    ┌────┬────┐
    │ TL │ TR │  bit 3 (0b1000)  bit 2 (0b0100)
    ├────┼────┤
    │ BL │ BR │  bit 1 (0b0010)  bit 0 (0b0001)
    └────┴────┘

    Examples:
        0b1111 = all solid (full block)
        0b1100 = top half solid (platform)
        0b0011 = bottom half solid
"""

from typing import Optional, TypedDict


class TileDefinition(TypedDict):
    """Definition for a tile type."""

    sprite_sheet: str  # Which sprite sheet to use
    sprite_name: Optional[str]  # Name of sprite in the sheet (None for empty tiles)
    collision_mask: int  # 4-bit mask for quadrant collision


# Quadrant bit masks
QUAD_TL = 0b1000  # Top-left quadrant
QUAD_TR = 0b0100  # Top-right quadrant
QUAD_BL = 0b0010  # Bottom-left quadrant
QUAD_BR = 0b0001  # Bottom-right quadrant

# Common collision patterns
MASK_EMPTY = 0b0000  # No collision
MASK_FULL = 0b1111  # All quadrants solid
MASK_TOP_HALF = 0b1100  # Top two quadrants solid
MASK_BOTTOM_HALF = 0b0011  # Bottom two quadrants solid
MASK_LEFT_HALF = 0b1010  # Left two quadrants solid
MASK_RIGHT_HALF = 0b0101  # Right two quadrants solid

# Tile type constants
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_BRICK = 2
TILE_PIPE = 3

# Tile definitions registry
TILE_DEFS: dict[int, TileDefinition] = {
    TILE_EMPTY: {
        "sprite_sheet": "background",
        "sprite_name": None,
        "collision_mask": MASK_EMPTY,
    },
    TILE_GROUND: {
        "sprite_sheet": "background",
        "sprite_name": "ground",
        "collision_mask": MASK_FULL,
    },
    TILE_BRICK: {
        "sprite_sheet": "background",
        "sprite_name": "brick",
        "collision_mask": MASK_FULL,
    },
    TILE_PIPE: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_left",
        "collision_mask": MASK_FULL,
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


def is_quadrant_solid(tile_def: TileDefinition, quadrant_x: int, quadrant_y: int) -> bool:
    """Check if a specific quadrant of a tile is solid using bitwise operations.

    Args:
        tile_def: The tile definition to check
        quadrant_x: X position within tile (0=left, 1=right)
        quadrant_y: Y position within tile (0=bottom, 1=top)

    Returns:
        True if the quadrant is solid

    Example:
        For a tile with mask 0b1100 (top half solid):
        - is_quadrant_solid(tile, 0, 1) -> True  (top-left)
        - is_quadrant_solid(tile, 0, 0) -> False (bottom-left)
    """
    # Convert quadrant coordinates to bit position (0-3)
    # Layout: TL=3, TR=2, BL=1, BR=0
    bit_pos = quadrant_y * 2 + quadrant_x

    # Create a mask for this specific quadrant
    quadrant_mask = 1 << bit_pos

    # Use bitwise AND to test if the bit is set
    return (tile_def["collision_mask"] & quadrant_mask) != 0