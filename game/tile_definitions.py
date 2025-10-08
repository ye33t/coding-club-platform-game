"""Tile definitions mapping tile slugs to properties.

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
    """Definition for a tile type referenced by slug."""

    sprite_sheet: str
    sprite_name: str | None
    collision_mask: int


_TILE_LIBRARY = load_tiles()


def _build_tile_definition(record: TileDefinitionRecord) -> TileDefinition:
    return TileDefinition(
        sprite_sheet=record.sprite_sheet,
        sprite_name=record.sprite,
        collision_mask=record.collision_mask,
    )


TILE_DEFS: Dict[str, TileDefinition] = {
    tile.slug: _build_tile_definition(tile) for tile in _TILE_LIBRARY.tiles.values()
}

SIMPLE_TILES: Dict[str, str] = dict(_TILE_LIBRARY.simple_tiles)

_EMPTY_TILE_SLUG = "empty"
if _EMPTY_TILE_SLUG not in TILE_DEFS:
    raise RuntimeError("Tile slug 'empty' must be defined in tile assets.")

if "." not in SIMPLE_TILES:
    SIMPLE_TILES["."] = _EMPTY_TILE_SLUG


def empty_tile_slug() -> str:
    """Return the slug used for empty space tiles."""

    return _EMPTY_TILE_SLUG


def require_tile(tile_slug: str) -> str:
    """Ensure a tile slug is defined, returning it for convenience."""

    if tile_slug not in TILE_DEFS:
        raise KeyError(f"Tile '{tile_slug}' is not defined in tile assets.")
    return tile_slug


def simple_tile_mapping() -> Dict[str, str]:
    """Return mapping from simple layout characters to tile slugs."""

    return dict(SIMPLE_TILES)


def get_tile_definition(tile_slug: str) -> Optional[TileDefinition]:
    """Get the definition for a tile slug."""

    return TILE_DEFS.get(tile_slug)


def is_quadrant_solid(
    tile_def: TileDefinition, quadrant_x: int, quadrant_y: int
) -> bool:
    """Check if a specific quadrant of a tile is solid."""

    bit_pos = quadrant_y * 2 + quadrant_x
    quadrant_mask = 1 << bit_pos
    return (tile_def["collision_mask"] & quadrant_mask) != 0


__all__ = [
    "TileDefinition",
    "TILE_DEFS",
    "empty_tile_slug",
    "require_tile",
    "get_tile_definition",
    "is_quadrant_solid",
    "simple_tile_mapping",
]
