"""Detect when Mario falls below the screen and trigger death."""

from ..constants import TILE_SIZE
from .base import PhysicsContext, PhysicsProcessor
from .config import DEATH_LEAP_VELOCITY

DEATH_LEAP_HEIGHT = TILE_SIZE * 2  # Jump 2 tiles up when dying


class DeathTriggerProcessor(PhysicsProcessor):
    """Detects when Mario falls below the screen and triggers death.

    This processor:
    - Checks if Mario has fallen below y=0 (bottom of screen)
    - Triggers the death sequence
    - Sets initial death leap velocity
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check if Mario should die."""
        mario_state = context.mario_state

        # Don't re-trigger if already dying
        if mario_state.is_dying:
            return context

        # Check if Mario fell below the screen
        if mario_state.y < 0:
            # Trigger death sequence
            mario_state.is_dying = True
            # Set death leap velocity from config
            mario_state.death_leap_velocity = DEATH_LEAP_VELOCITY
            mario_state.vy = (
                mario_state.death_leap_velocity
            )  # Start the leap immediately
            mario_state.on_ground = False

        return context
