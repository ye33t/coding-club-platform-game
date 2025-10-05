"""Detect when Mario falls below the screen and raise death event."""

from .base import PhysicsContext, PhysicsProcessor
from .events import DeathEvent


class DeathEventProcessor(PhysicsProcessor):
    """Detects when Mario falls below the screen and raises a death event.

    This processor:
    - Checks if Mario has fallen below y=0 (bottom of screen)
    - Raises DeathEvent which will short-circuit the pipeline
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check if Mario should die."""
        mario_state = context.mario_state

        # Check if Mario fell below the screen
        if mario_state.y < 0:
            # Raise death event
            context.event = DeathEvent()

        return context
