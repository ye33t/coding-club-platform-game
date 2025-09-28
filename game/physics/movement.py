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
        mario_state = context.mario_state
        intent = context.mario_intent

        # Skip movement processing if dying
        if mario_state.is_dying:
            return context

        # If no horizontal movement intent, apply friction
        if not intent.move_left and not intent.move_right:
            mario_state.vx *= FRICTION

            # Stop completely if velocity is very small
            if abs(mario_state.vx) < 1.0:
                mario_state.vx = 0.0

        return context
