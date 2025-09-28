"""Detect when Mario falls below the screen and trigger death."""

from ..constants import TILE_SIZE
from .base import PhysicsContext, PhysicsProcessor

DEATH_LEAP_HEIGHT = TILE_SIZE * 3  # Jump 3 tiles up when dying


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
            # Calculate velocity needed to jump 3 tiles
            # Using kinematic equation: v² = u² + 2as
            # We want to reach 3 tiles high, so v=0 at peak
            # 0 = u² - 2g*h => u = sqrt(2gh)
            # But we'll use a simple fixed velocity for predictable behavior
            mario_state.death_leap_velocity = 150.0  # Will jump approximately 3 tiles
            mario_state.vy = (
                mario_state.death_leap_velocity
            )  # Start the leap immediately
            mario_state.on_ground = False

        return context
