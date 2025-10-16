"""Terrain behavior markers for the castle end-of-level sequence."""

from __future__ import annotations

from dataclasses import dataclass

from ..constants import TILE_SIZE
from .base import BehaviorContext, TerrainBehavior


@dataclass(slots=True)
class CastleExitBehavior(TerrainBehavior):
    """Marker behavior for castle sequence anchors."""

    role: str
    offset_x: float = 0.0
    offset_y: float = 0.0
    start_offset_y: float | None = None

    def __post_init__(self) -> None:
        role = self.role.lower()
        if role not in {"walk", "flag"}:
            raise ValueError(
                "castle_exit behavior 'role' must be either 'walk' or 'flag'"
            )
        self.role = role

    def process(self, context: BehaviorContext) -> None:  # noqa: D401
        """Castle markers do not perform runtime processing."""
        return

    def world_x(self, tile_x: int) -> float:
        """Compute world X coordinate for the tile with offset applied."""
        return tile_x * TILE_SIZE + self.offset_x

    def world_y(self, tile_y: int) -> float:
        """Compute world Y coordinate for the tile with offset applied."""
        return tile_y * TILE_SIZE + self.offset_y

    def initial_flag_y(self, tile_y: int) -> float:
        """Get initial bottom Y position for the raising castle flag."""
        final_y = self.world_y(tile_y)
        if self.start_offset_y is not None:
            return final_y + self.start_offset_y
        return final_y - TILE_SIZE
