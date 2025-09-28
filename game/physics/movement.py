"""Handle movement physics including friction and deceleration."""

from .base import PhysicsContext, PhysicsProcessor

FRICTION = 0.85  # Speed multiplier when decelerating


class MovementProcessor(PhysicsProcessor):
    """Handles horizontal movement physics.

    This processor manages:
    - Friction when no input is given
    - Deceleration
    - Stopping when velocity is very small
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process movement physics."""
        state = context.mario
        intent = context.mario_intent

        # Skip movement processing if dying
        if state.is_dying:
            return context

        # If no horizontal movement intent, apply friction
        if not intent.move_left and not intent.move_right:
            state.vx *= FRICTION

            # Stop completely if velocity is very small
            if abs(state.vx) < 1.0:
                state.vx = 0.0

        return context
