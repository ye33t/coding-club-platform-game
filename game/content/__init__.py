"""Helpers for loading structured asset metadata."""

from .loader import SpriteLibrary, TileLibrary, load_sprite_sheets, load_tiles
from .sprite_sheet import SpriteSheet
from .sprites import sprites
from .tile_definitions import (
    TILE_DEFS,
    empty_tile_slug,
    get_tile_definition,
    is_quadrant_solid,
    require_tile,
    simple_tile_mapping,
)
from .types import (
    SpriteFrame,
    SpriteKey,
    SpriteSheetDef,
    TileAnimation,
    TileAnimationFrame,
    TileConfig,
    TileDefinition,
)

__all__ = [
    "SpriteLibrary",
    "TileLibrary",
    "SpriteSheet",
    "SpriteKey",
    "SpriteFrame",
    "SpriteSheetDef",
    "TileAnimationFrame",
    "TileAnimation",
    "TileConfig",
    "TileDefinition",
    "TILE_DEFS",
    "empty_tile_slug",
    "require_tile",
    "simple_tile_mapping",
    "get_tile_definition",
    "is_quadrant_solid",
    "load_sprite_sheets",
    "load_tiles",
    "sprites",
]
