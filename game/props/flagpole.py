"""Flagpole prop responsible for the decorative flag sprite."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..constants import SUB_TILE_SIZE, TILE_SIZE
from ..effects import SpriteEffect
from ..terrain.flagpole import FlagpoleBehavior
from .base import Prop


@dataclass
class FlagpoleState:
    effect: SpriteEffect
    world_x: float
    world_y: float
    base_y: float
    complete: bool = False


class FlagpoleProp(Prop):
    """Maintains the static flag sprite at the top of the flagpole."""

    def __init__(self) -> None:
        self._state: Optional[FlagpoleState] = None

    @property
    def complete(self) -> bool:
        return self._state.complete if self._state else False

    def spawn(self, world) -> None:  # noqa: D401
        """Create the decorative flag if the level contains a flagpole."""
        flagpole_tiles = [
            instance
            for instance in world.level.terrain_manager.instances.values()
            if isinstance(instance.behavior, FlagpoleBehavior)
        ]

        if not flagpole_tiles:
            return

        top_tile = max(flagpole_tiles, key=lambda tile: tile.y)
        pole_x = top_tile.x * TILE_SIZE + SUB_TILE_SIZE - 1
        pole_top_y = (top_tile.y - 1) * TILE_SIZE

        # Position flag so its left edge sits one tile to the left of the pole.
        flag_world_x = pole_x - TILE_SIZE
        # Keep the sprite bottom aligned with the pole top.
        flag_world_y = pole_top_y
        flag_base_y = min(tile.y for tile in flagpole_tiles) * TILE_SIZE

        self._state = FlagpoleState(
            effect=SpriteEffect(
                sprite_sheet="objects",
                sprite_name="flag",
                world_x=flag_world_x,
                world_y=flag_world_y,
                z_index=5,
            ),
            world_x=flag_world_x,
            world_y=flag_world_y,
            base_y=flag_base_y,
        )

        world.effects.spawn(self._state.effect)

    def reset(self, world) -> None:
        """Rebuild the decorative flag after a world reset."""
        self.destroy()
        self.spawn(world)

    def destroy(self) -> None:
        if self._state:
            self._state.effect.deactivate()
        self._state = None

    def descend(self, dt: float) -> None:
        """Slide the flag downward toward the base."""
        if self._state is None:
            return

        from ..physics.config import FLAGPOLE_DESCENT_SPEED

        self._state.complete = False

        next_y = self._state.world_y - FLAGPOLE_DESCENT_SPEED * dt
        if next_y <= self._state.base_y:
            self._state.world_y = self._state.base_y
            self._state.effect.set_position(self._state.world_x, self._state.world_y)
            self._state.complete = True
            return

        self._state.world_y = next_y
        self._state.effect.set_position(self._state.world_x, self._state.world_y)
