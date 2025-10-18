"""Tile definition registry backed by asset configuration."""

from __future__ import annotations

from typing import Dict, Optional

from .loader import load_tiles
from .types import TileConfig, TileDefinition

_TILE_LIBRARY = load_tiles()


def _build_tile_definition(record: TileConfig) -> TileDefinition:
    return TileDefinition(
        sprite_sheet=record.sprite_sheet,
        sprite_name=record.sprite,
        collision_mask=record.collision_mask,
        animation=record.animation,
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
    return (tile_def.collision_mask & quadrant_mask) != 0


__all__ = [
    "TileDefinition",
    "TILE_DEFS",
    "empty_tile_slug",
    "require_tile",
    "simple_tile_mapping",
    "get_tile_definition",
    "is_quadrant_solid",
]
