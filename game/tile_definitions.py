"""Tile definitions mapping tile IDs to properties.

Collision Masks:
    Each tile (16x16 pixels) is divided into 4 quadrants (8x8 pixels each).
    A 4-bit mask represents which quadrants are solid:

    ┌────┬────┐
    │ TL │ TR │  bit 3 (0b1000)  bit 2 (0b0100)
    ├────┼────┤
    │ BL │ BR │  bit 1 (0b0010)  bit 0 (0b0001)
    └────┴────┘

    Examples:
        0b1111 = all solid (full tile)
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

# Basic terrain blocks
TILE_GROUND = 10
TILE_BRICK = 20
TILE_BRICK_TOP = 30
TILE_BLOCK = 40
TILE_BLOCK_FLAT = 50
TILE_EARTH = 60
TILE_BRIDGE = 70
TILE_ROCKS = 80
TILE_SAND = 90
TILE_SAND_WAVE = 100
TILE_SAND_LINES = 110
TILE_SAND_DUNE = 120
TILE_VOID = 130

# Architecture
TILE_ARCH_LEFT = 140
TILE_ARCH_CENTER = 150
TILE_ARCH_RIGHT = 160
TILE_BATTLEMENT = 170
TILE_BATTLEMENT_1 = 180
TILE_BRIDGE_RAILS = 190

# Pipes (vertical)
TILE_PIPE_LEFT = 200
TILE_PIPE_RIGHT = 210
TILE_PIPE_MOUTH_LEFT = 220
TILE_PIPE_MOUTH_RIGHT = 230

# Pipes (horizontal)
TILE_PIPE_HORIZONTAL_TOP = 240
TILE_PIPE_HORIZONTAL_BOTTOM = 250
TILE_PIPE_HORIZONTAL_MOUTH_TOP = 260
TILE_PIPE_HORIZONTAL_MOUTH_BOTTOM = 270
TILE_PIPE_JUNCTION_TOP = 280
TILE_PIPE_JUNCTION_BOTTOM = 290

# Cannons
TILE_CANNON_TOP = 300
TILE_CANNON_CENTER = 310
TILE_CANNON_BOTTOM = 320

# Conveyors
TILE_CONVEYOR_CORNER_LEFT = 330
TILE_CONVEYOR_HORIZONTAL = 340
TILE_CONVEYOR_RIGHT = 350
TILE_CONVEYOR_VERTICAL = 360

# Climbing
TILE_LADDER = 370
TILE_BEANSTALK = 380

# Mounds/Hills
TILE_MOUND_TOP = 390
TILE_MOUND_LEFT_45 = 400
TILE_MOUND_LEFT = 410
TILE_MOUND_CENTER = 420
TILE_MOUND_RIGHT = 430
TILE_MOUND_RIGHT_45 = 440

# Decoration (solid)
TILE_TREETOP_LEFT = 450
TILE_TREETOP_CENTER = 460
TILE_TREETOP_RIGHT = 470
TILE_MUSHROOM_LEFT = 480
TILE_MUSHROOM_CENTER = 490
TILE_MUSHROOM_RIGHT = 500
TILE_BUSH_LEFT = 510
TILE_BUSH_CENTER = 520
TILE_BUSH_RIGHT = 530
TILE_LEAVES = 540

# Lollipops
TILE_LOLLIPOP_TOP = 550
TILE_LOLLIPOP = 560
TILE_LOLLIPOP_BOTTOM = 570

# Flagpole
TILE_FLAGPOLE_TOP = 580
TILE_FLAGPOLE = 590
TILE_FLAG = 600

# Clouds
TILE_CLOUD_TOP_LEFT = 610
TILE_CLOUD_TOP = 620
TILE_CLOUD_TOP_RIGHT = 630
TILE_CLOUD_BOTTOM_LEFT = 640
TILE_CLOUD_BOTTOM = 650
TILE_CLOUD_BOTTOM_RIGHT = 660
TILE_CLOUD_BLOCK = 670

# Water
TILE_WATER_TOP = 680
TILE_WATER = 690

# Other
TILE_PIANO = 700

# Misc
TILE_ITEM_BOX = 710
TILE_COIN = 720
TILE_AXE = 730

# Tile definitions registry
TILE_DEFS: dict[int, TileDefinition] = {
    TILE_EMPTY: {
        "sprite_sheet": "background",
        "sprite_name": None,
        "collision_mask": MASK_EMPTY,
    },
    # Basic terrain
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
    TILE_BRICK_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "brick_top",
        "collision_mask": MASK_FULL,
    },
    TILE_BLOCK: {
        "sprite_sheet": "background",
        "sprite_name": "block",
        "collision_mask": MASK_FULL,
    },
    TILE_BLOCK_FLAT: {
        "sprite_sheet": "background",
        "sprite_name": "block_flat",
        "collision_mask": MASK_FULL,
    },
    TILE_EARTH: {
        "sprite_sheet": "background",
        "sprite_name": "earth",
        "collision_mask": MASK_FULL,
    },
    TILE_BRIDGE: {
        "sprite_sheet": "background",
        "sprite_name": "bridge",
        "collision_mask": MASK_TOP_HALF,
    },
    TILE_ROCKS: {
        "sprite_sheet": "background",
        "sprite_name": "rocks",
        "collision_mask": MASK_FULL,
    },
    # Sand
    TILE_SAND: {
        "sprite_sheet": "background",
        "sprite_name": "sand",
        "collision_mask": MASK_FULL,
    },
    TILE_SAND_WAVE: {
        "sprite_sheet": "background",
        "sprite_name": "sand_wave",
        "collision_mask": MASK_FULL,
    },
    TILE_SAND_LINES: {
        "sprite_sheet": "background",
        "sprite_name": "sand_lines",
        "collision_mask": MASK_FULL,
    },
    TILE_SAND_DUNE: {
        "sprite_sheet": "background",
        "sprite_name": "sand_dune",
        "collision_mask": MASK_FULL,
    },
    # Arches
    TILE_ARCH_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "arch_left",
        "collision_mask": MASK_LEFT_HALF,
    },
    TILE_ARCH_CENTER: {
        "sprite_sheet": "background",
        "sprite_name": "arch_center",
        "collision_mask": MASK_EMPTY,
    },
    TILE_ARCH_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "arch_right",
        "collision_mask": MASK_RIGHT_HALF,
    },
    TILE_VOID: {
        "sprite_sheet": "background",
        "sprite_name": "void",
        "collision_mask": MASK_EMPTY,
    },
    # Battlements
    TILE_BATTLEMENT: {
        "sprite_sheet": "background",
        "sprite_name": "battlement",
        "collision_mask": MASK_FULL,
    },
    TILE_BATTLEMENT_1: {
        "sprite_sheet": "background",
        "sprite_name": "battlement_1",
        "collision_mask": MASK_FULL,
    },
    # Bridge rails (decoration, no collision)
    TILE_BRIDGE_RAILS: {
        "sprite_sheet": "background",
        "sprite_name": "bridge_rails",
        "collision_mask": MASK_EMPTY,
    },
    # Pipes (vertical)
    TILE_PIPE_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_left",
        "collision_mask": MASK_FULL,
    },
    TILE_PIPE_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_right",
        "collision_mask": MASK_FULL,
    },
    TILE_PIPE_MOUTH_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_mouth_left",
        "collision_mask": MASK_FULL,
    },
    TILE_PIPE_MOUTH_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_mouth_right",
        "collision_mask": MASK_FULL,
    },
    # Pipes (horizontal)
    TILE_PIPE_HORIZONTAL_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_horizontal_top",
        "collision_mask": MASK_FULL,
    },
    TILE_PIPE_HORIZONTAL_BOTTOM: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_horizontal_bottom",
        "collision_mask": MASK_FULL,
    },
    TILE_PIPE_HORIZONTAL_MOUTH_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_horizontal_mouth_top",
        "collision_mask": MASK_FULL,
    },
    TILE_PIPE_HORIZONTAL_MOUTH_BOTTOM: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_horizontal_mouth_bottom",
        "collision_mask": MASK_FULL,
    },
    # Pipe junction
    TILE_PIPE_JUNCTION_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_junction_top",
        "collision_mask": MASK_FULL,
    },
    TILE_PIPE_JUNCTION_BOTTOM: {
        "sprite_sheet": "background",
        "sprite_name": "pipe_junction_bottom",
        "collision_mask": MASK_FULL,
    },
    # Cannon
    TILE_CANNON_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "cannon_top",
        "collision_mask": MASK_FULL,
    },
    TILE_CANNON_CENTER: {
        "sprite_sheet": "background",
        "sprite_name": "cannon_center",
        "collision_mask": MASK_FULL,
    },
    TILE_CANNON_BOTTOM: {
        "sprite_sheet": "background",
        "sprite_name": "cannon_bottom",
        "collision_mask": MASK_FULL,
    },
    # Climbing
    TILE_LADDER: {
        "sprite_sheet": "background",
        "sprite_name": "ladder",
        "collision_mask": MASK_FULL,
    },
    TILE_BEANSTALK: {
        "sprite_sheet": "background",
        "sprite_name": "beanstalk",
        "collision_mask": MASK_FULL,
    },
    # Mushroom
    TILE_MUSHROOM_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "mushroom_left",
        "collision_mask": MASK_FULL,
    },
    TILE_MUSHROOM_CENTER: {
        "sprite_sheet": "background",
        "sprite_name": "mushroom_center",
        "collision_mask": MASK_FULL,
    },
    TILE_MUSHROOM_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "mushroom_right",
        "collision_mask": MASK_FULL,
    },
    # Decoration
    TILE_MOUND_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "mound_top",
        "collision_mask": MASK_EMPTY,
    },
    TILE_MOUND_LEFT_45: {
        "sprite_sheet": "background",
        "sprite_name": "mound_left_45",
        "collision_mask": MASK_EMPTY,
    },
    TILE_MOUND_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "mound_left",
        "collision_mask": MASK_EMPTY,
    },
    TILE_MOUND_CENTER: {
        "sprite_sheet": "background",
        "sprite_name": "mound_center",
        "collision_mask": MASK_EMPTY,
    },
    TILE_MOUND_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "mound_right",
        "collision_mask": MASK_EMPTY,
    },
    TILE_MOUND_RIGHT_45: {
        "sprite_sheet": "background",
        "sprite_name": "mound_right_45",
        "collision_mask": MASK_EMPTY,
    },
    # Tree
    TILE_TREETOP_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "treetop_left",
        "collision_mask": MASK_EMPTY,
    },
    TILE_TREETOP_CENTER: {
        "sprite_sheet": "background",
        "sprite_name": "treetop_center",
        "collision_mask": MASK_EMPTY,
    },
    TILE_TREETOP_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "treetop_right",
        "collision_mask": MASK_EMPTY,
    },
    # Bush
    TILE_BUSH_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "bush_left",
        "collision_mask": MASK_EMPTY,
    },
    TILE_BUSH_CENTER: {
        "sprite_sheet": "background",
        "sprite_name": "bush_center",
        "collision_mask": MASK_EMPTY,
    },
    TILE_BUSH_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "bush_right",
        "collision_mask": MASK_EMPTY,
    },
    TILE_LEAVES: {
        "sprite_sheet": "background",
        "sprite_name": "leaves",
        "collision_mask": MASK_EMPTY,
    },
    # Conveyors
    TILE_CONVEYOR_CORNER_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "conveyor_corner_left",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CONVEYOR_HORIZONTAL: {
        "sprite_sheet": "background",
        "sprite_name": "conveyor_horizontal",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CONVEYOR_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "conveyor_right",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CONVEYOR_VERTICAL: {
        "sprite_sheet": "background",
        "sprite_name": "conveyor_vertical",
        "collision_mask": MASK_EMPTY,
    },
    # Lollipops
    TILE_LOLLIPOP_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "lollipop_top",
        "collision_mask": MASK_EMPTY,
    },
    TILE_LOLLIPOP: {
        "sprite_sheet": "background",
        "sprite_name": "lollipop",
        "collision_mask": MASK_EMPTY,
    },
    TILE_LOLLIPOP_BOTTOM: {
        "sprite_sheet": "background",
        "sprite_name": "lollipop_bottom",
        "collision_mask": MASK_EMPTY,
    },
    # Flagpole
    TILE_FLAGPOLE_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "flagpole_top",
        "collision_mask": MASK_EMPTY,
    },
    TILE_FLAGPOLE: {
        "sprite_sheet": "background",
        "sprite_name": "flagpole",
        "collision_mask": MASK_EMPTY,
    },
    TILE_FLAG: {
        "sprite_sheet": "other",
        "sprite_name": "flag",
        "collision_mask": MASK_EMPTY,
    },
    # Clouds
    TILE_CLOUD_TOP_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "cloud_top_left",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CLOUD_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "cloud_top",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CLOUD_TOP_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "cloud_top_right",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CLOUD_BOTTOM_LEFT: {
        "sprite_sheet": "background",
        "sprite_name": "cloud_bottom_left",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CLOUD_BOTTOM: {
        "sprite_sheet": "background",
        "sprite_name": "cloud_bottom",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CLOUD_BOTTOM_RIGHT: {
        "sprite_sheet": "background",
        "sprite_name": "cloud_bottom_right",
        "collision_mask": MASK_EMPTY,
    },
    TILE_CLOUD_BLOCK: {
        "sprite_sheet": "background",
        "sprite_name": "cloud_block",
        "collision_mask": MASK_EMPTY,
    },
    # Water
    TILE_WATER_TOP: {
        "sprite_sheet": "background",
        "sprite_name": "water_top",
        "collision_mask": MASK_EMPTY,
    },
    TILE_WATER: {
        "sprite_sheet": "background",
        "sprite_name": "water",
        "collision_mask": MASK_EMPTY,
    },
    # Other
    TILE_PIANO: {
        "sprite_sheet": "background",
        "sprite_name": "piano",
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


def is_quadrant_solid(
    tile_def: TileDefinition, quadrant_x: int, quadrant_y: int
) -> bool:
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
