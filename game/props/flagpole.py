"""Flagpole prop responsible for the decorative flag sprite."""

from __future__ import annotations

from typing import Optional

from ..constants import SUB_TILE_SIZE, TILE_SIZE
from ..effects import SpriteEffect
from ..terrain.flagpole import FlagpoleBehavior
from .base import Prop


class FlagpoleProp(Prop):
    """Maintains the static flag sprite at the top of the flagpole."""

    def __init__(self) -> None:
        self._flag_effect: Optional[SpriteEffect] = None
        self._flag_world_x: Optional[float] = None
        self._flag_world_y: Optional[float] = None

    def spawn(self, world) -> None:  # noqa: D401
        """Create the decorative flag if the level contains a flagpole."""
        if not self._ensure_flag_position(world):
            return

        if self._flag_effect is not None:
            return

        assert self._flag_world_x is not None
        assert self._flag_world_y is not None

        flag_effect = SpriteEffect(
            sprite_sheet="other",
            sprite_name="flag",
            world_x=self._flag_world_x,
            world_y=self._flag_world_y,
            z_index=5,
        )
        world.effects.spawn(flag_effect)
        self._flag_effect = flag_effect

    def reset(self, world) -> None:
        """Rebuild the decorative flag after a world reset."""
        self.destroy()
        # Recalculate in case terrain changed during the reset.
        self._flag_world_x = None
        self._flag_world_y = None
        self.spawn(world)

    def destroy(self) -> None:
        if self._flag_effect:
            self._flag_effect.deactivate()
            self._flag_effect = None

    def _ensure_flag_position(self, world) -> bool:
        if self._flag_world_x is not None and self._flag_world_y is not None:
            return True

        flagpole_tiles = [
            instance
            for instance in world.level.terrain_manager.instances.values()
            if isinstance(instance.behavior, FlagpoleBehavior)
        ]

        if not flagpole_tiles:
            return False

        top_tile = max(flagpole_tiles, key=lambda tile: tile.y)
        pole_x = top_tile.x * TILE_SIZE + SUB_TILE_SIZE - 1
        pole_top_y = (top_tile.y - 1) * TILE_SIZE

        # Position flag so its left edge sits one tile to the left of the pole.
        self._flag_world_x = pole_x - TILE_SIZE
        # Keep the sprite bottom aligned with the pole top.
        self._flag_world_y = pole_top_y
        return True
