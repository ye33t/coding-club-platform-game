"""Shared dataclasses for sprite and tile asset metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple


@dataclass(frozen=True)
class SpriteKey:
    """Runtime metadata for a sprite referenced by slug."""

    sprite_sheet: str
    sprite_name: str


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
class TileAnimationFrame:
    """Single frame within an animated tile definition."""

    sprite: str
    frames: int

    def __post_init__(self) -> None:
        if self.frames <= 0:
            raise ValueError("Tile animation frame durations must be positive.")


@dataclass(frozen=True, slots=True)
class TileAnimation:
    """Animation metadata for tiles with multiple sprite frames."""

    frames: Tuple[TileAnimationFrame, ...]
    total_frames: int

    def sprite_for_tick(self, tick: int) -> str:
        """Resolve the sprite to use for the provided animation tick."""
        if not self.frames:
            raise ValueError("TileAnimation must contain at least one frame.")

        if self.total_frames <= 0:
            raise ValueError("TileAnimation total duration must be positive.")

        position = tick % self.total_frames
        cumulative = 0

        for frame in self.frames:
            cumulative += frame.frames
            if position < cumulative:
                return frame.sprite

        # Fallback: return the final sprite (should be unreachable)
        return self.frames[-1].sprite


@dataclass(frozen=True, slots=True)
class TileConfig:
    """Metadata for a single tile declared in TOML assets."""

    slug: str
    sprite_sheet: str
    sprite: str | None
    collision_mask: int
    category: str | None = None
    simple_key: str | None = None
    animation: TileAnimation | None = None


@dataclass(frozen=True, slots=True)
class TileDefinition:
    """Runtime metadata for a tile referenced by slug."""

    sprite_sheet: str
    sprite_name: str | None
    collision_mask: int
    category: str | None = None
    animation: TileAnimation | None = None

    def resolve_sprite_name(self, animation_tick: int) -> str | None:
        """Return the appropriate sprite for the provided animation tick."""
        if self.animation is not None:
            return self.animation.sprite_for_tick(animation_tick)
        return self.sprite_name
