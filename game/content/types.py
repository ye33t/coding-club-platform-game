"""Shared dataclasses for sprite and tile asset metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class SpriteFrame:
    """Normalized sprite metadata loaded from YAML definitions."""

    offset: tuple[int, int]
    size: tuple[int, int]


@dataclass(frozen=True, slots=True)
class SpriteSheetDef:
    """Sprite sheet configuration and the sprites it exposes."""

    name: str
    image: str | None
    sprites: Mapping[str, "SpriteFrame"]
    default_tile_size: tuple[int, int] | None = None
    colorkey: tuple[int, int, int] | str | None = None


@dataclass(frozen=True, slots=True)
class TileConfig:
    """Metadata for a single tile declared in TOML assets."""

    slug: str
    sprite_sheet: str
    sprite: str | None
    collision_mask: int
    category: str | None = None
    simple_key: str | None = None


@dataclass(frozen=True, slots=True)
class TileDefinition:
    """Runtime metadata for a tile referenced by slug."""

    sprite_sheet: str
    sprite_name: str | None
    collision_mask: int
