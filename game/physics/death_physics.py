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
        mario_state = context.mario_state

        # Only process if dying
        if not mario_state.is_dying:
            return context

        # Apply gravity to make Mario fall after the leap
        mario_state.vy -= GRAVITY * context.dt

        # No horizontal movement during death
        mario_state.vx = 0

        # Ensure we stay in dying state
        mario_state.on_ground = False

        return context
