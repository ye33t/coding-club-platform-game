from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TileDefinition:
    """Metadata for a single tile ID."""

    slug: str
    sprite_sheet: str
    sprite: str | None
    collision_mask: int
    category: str | None = None
