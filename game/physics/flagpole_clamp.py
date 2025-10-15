"""Clamp Mario against the flagpole during the end-level sequence."""

from ..constants import TILE_SIZE
from ..terrain.flagpole import FlagpoleBehavior
from .base import PhysicsContext, PhysicsProcessor


class FlagpoleClampProcessor(PhysicsProcessor):
    """Prevents Mario from passing through the flagpole column."""

    def process(self, context: PhysicsContext) -> PhysicsContext:
        mario = context.mario

        flagpole_instances = [
            instance
            for instance in context.level.terrain_manager.instances.values()
            if instance.screen == mario.screen
            and isinstance(instance.behavior, FlagpoleBehavior)
        ]

        if not flagpole_instances:
            return context

        flagpole_x = flagpole_instances[0].x
        flagpole_center_x = flagpole_x * TILE_SIZE + (TILE_SIZE / 2)
        clamp_x = flagpole_center_x - mario.width

        if mario.x > clamp_x:
            mario.x = clamp_x
            if mario.vx > 0:
                mario.vx = 0.0

        return context
