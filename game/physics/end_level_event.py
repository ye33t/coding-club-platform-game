"""Detect when Mario touches the flagpole and raise end level event."""

from ..constants import TILE_SIZE
from ..terrain import FlagpoleBehavior
from .base import PhysicsContext, PhysicsProcessor
from .config import FLAGPOLE_TRIGGER_DISTANCE
from .events import EndLevelEvent


class EndLevelEventProcessor(PhysicsProcessor):
    """Detects when Mario touches the flagpole and raises an end level event.

    This processor:
    - Checks if Mario is on same screen as flagpole
    - Checks if Mario is within trigger distance of flagpole center
    - Raises EndLevelEvent which will short-circuit the pipeline
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check if Mario should trigger end level."""
        mario_state = context.mario_state

        # Find all flagpole behavior instances on Mario's screen
        flagpole_instances = [
            instance
            for instance in context.level.terrain_manager.instances.values()
            if instance.screen == mario_state.screen
            and isinstance(instance.behavior, FlagpoleBehavior)
        ]

        if not flagpole_instances:
            return context  # No flagpole on this screen

        # Get flagpole X position (all instances have same x after validation)
        flagpole_x = flagpole_instances[0].x
        flagpole_center_x = flagpole_x * TILE_SIZE + (TILE_SIZE / 2)

        mario_right = mario_state.x + mario_state.width

        # Check if Mario is within trigger distance using his right edge
        if mario_right >= (flagpole_center_x - FLAGPOLE_TRIGGER_DISTANCE):
            # Calculate base Y position (minimum y among all flagpole instances)
            min_y = min(instance.y for instance in flagpole_instances)
            flagpole_base_y = min_y * TILE_SIZE

            # Raise end level event
            context.event = EndLevelEvent(
                flagpole_x=flagpole_center_x, flagpole_base_y=flagpole_base_y
            )

        return context
