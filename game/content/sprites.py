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
    sprites: Mapping[str, SpriteFrame]
    default_tile_size: tuple[int, int] | None = None
    colorkey: tuple[int, int, int] | str | None = None
