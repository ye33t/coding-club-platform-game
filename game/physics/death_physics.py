"""Handle physics during death animation."""

from .base import PhysicsContext, PhysicsProcessor
from .gravity import GRAVITY


class DeathPhysicsProcessor(PhysicsProcessor):
    """Handles special physics during death animation.

    This processor:
    - Applies gravity during death fall
    - Ensures no other physics interfere
    - Runs early in pipeline to override other processors
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process death physics."""
        state = context.mario

        # Only process if dying
        if not state.is_dying:
            return context

        # Apply gravity to make Mario fall after the leap
        state.vy -= GRAVITY * context.dt

        # No horizontal movement during death
        state.vx = 0

        # Ensure we stay in dying state
        state.on_ground = False

        return context
