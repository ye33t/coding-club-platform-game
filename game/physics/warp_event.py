"""Detect when Mario enters a warp pipe and raise warp event."""

from ..constants import TILE_SIZE
from ..terrain.warp import WarpBehavior
from .base import PhysicsContext, PhysicsProcessor
from .events import WarpEvent


class WarpEventProcessor(PhysicsProcessor):
    """Detects when Mario enters a warp pipe and raises a warp event.

    This processor:
    - Checks if down key is pressed while on ground
    - Checks if Mario is standing on a warp tile
    - Raises WarpEvent which will short-circuit the pipeline
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check if Mario should warp."""
        mario = context.mario
        intent = mario.intent

        # Check if down key is pressed while on ground
        if not intent.duck or not mario.on_ground:
            return context

        # Get tile below Mario (the one he's standing on)
        tile_x = int(mario.x // TILE_SIZE)
        tile_y = int(mario.y // TILE_SIZE) - 1

        # Check for warp behavior
        instance = context.level.terrain_manager.get_instance(
            mario.screen, tile_x, tile_y
        )

        if instance and instance.behavior:
            if isinstance(instance.behavior, WarpBehavior):
                # Raise warp event with the behavior data
                context.event = WarpEvent(warp_behavior=instance.behavior)

        return context
