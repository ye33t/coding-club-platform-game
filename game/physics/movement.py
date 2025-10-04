"""Handle movement physics including friction and deceleration."""

from .base import PhysicsContext, PhysicsProcessor
from .constants import MIN_FRICTION


class MovementProcessor(PhysicsProcessor):
    """Handles horizontal movement physics.

    This processor manages:
    - Simple step-function friction for natural deceleration
    - Instant stop below threshold, constant friction above
    """

    STOP_THRESHOLD = 30.0  # px/s - instant stop below this speed

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process movement physics."""
        mario_state = context.mario_state
        intent = context.mario_intent

        # Skip movement processing if dying
        if mario_state.is_dying:
            return context

        # If no horizontal movement intent, apply friction
        if not intent.move_left and not intent.move_right:
            speed = abs(mario_state.vx)

            # Simple step function:
            # Below threshold: instant stop
            # Above threshold: constant friction
            if speed < self.STOP_THRESHOLD:
                mario_state.vx = 0.0
            else:
                mario_state.vx *= MIN_FRICTION

        return context
