"""Tile definitions mapping tile IDs to properties.

Collision Masks:
    Each tile (16x16 pixels) is divided into 4 quadrants (8x8 pixels each).
    A 4-bit mask represents which quadrants are solid:

    ┌────┬────┐
    │ TL │ TR │  bit 3 (0b1000)  bit 2 (0b0100)
    ├────┼────┤
    │ BL │ BR │  bit 1 (0b0010)  bit 0 (0b0001)
    └────┴────┘
"""

from __future__ import annotations

from typing import Dict, Optional, TypedDict

from .content import load_tiles
from .content.tiles import TileDefinition as TileDefinitionRecord


class TileDefinition(TypedDict):
    """Definition for a tile type."""

    sprite_sheet: str
    sprite_name: str | None
    collision_mask: int


# Quadrant bit masks
QUAD_TL = 0b1000  # Top-left quadrant
QUAD_TR = 0b0100  # Top-right quadrant
QUAD_BL = 0b0010  # Bottom-left quadrant
QUAD_BR = 0b0001  # Bottom-right quadrant

_TILE_LIBRARY = load_tiles()


def _build_tile_definition(record: TileDefinitionRecord) -> TileDefinition:
    return TileDefinition(
        sprite_sheet=record.sprite_sheet,
        sprite_name=record.sprite,
        collision_mask=record.collision_mask,
    )


TILE_DEFS: Dict[int, TileDefinition] = {
    tile.id: _build_tile_definition(tile) for tile in _TILE_LIBRARY.tiles_by_id.values()
}


def _register_constants():
    # Collision mask aliases
    for alias, value in _TILE_LIBRARY.collision_masks.items():
        name = f"MASK_{alias.upper()}"
        if name in globals():
            raise ValueError(f"Duplicate collision mask constant '{name}'")
        globals()[name] = value

    # Tile ID constants
    for tile in _TILE_LIBRARY.tiles_by_id.values():
        const_name = f"TILE_{tile.slug.upper()}"
        if const_name in globals():
            raise ValueError(f"Duplicate tile constant '{const_name}'")
        globals()[const_name] = tile.id


_register_constants()


def get_tile_definition(tile_type: int) -> Optional[TileDefinition]:
    """Get the definition for a tile type."""

    return TILE_DEFS.get(tile_type)


def is_quadrant_solid(
    tile_def: TileDefinition, quadrant_x: int, quadrant_y: int
) -> bool:
    """Check if a specific quadrant of a tile is solid using bitwise operations."""

    bit_pos = quadrant_y * 2 + quadrant_x
    quadrant_mask = 1 << bit_pos
    return (tile_def["collision_mask"] & quadrant_mask) != 0
