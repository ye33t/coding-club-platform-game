"""Handle movement physics including friction and deceleration."""

from .base import PhysicsContext, PhysicsProcessor
from .config import MIN_FRICTION, MAX_FRICTION, FRICTION_SPEED_RANGE, STOP_THRESHOLD


class MovementProcessor(PhysicsProcessor):
    """Handles horizontal movement physics.

    This processor manages:
    - Speed-based friction for natural deceleration
    - More friction at low speeds (walking), less at high speeds (running)
    - Instant stop below threshold
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
            speed = abs(mario_state.vx)

            # Below threshold: instant stop
            if speed < STOP_THRESHOLD:
                mario_state.vx = 0.0
            else:
                # Speed-based friction:
                # At low speeds (walking): MAX_FRICTION (more friction, less slide)
                # At high speeds (running): MIN_FRICTION (less friction, more slide)
                friction_factor = min(speed / FRICTION_SPEED_RANGE, 1.0)
                friction = MAX_FRICTION + (MIN_FRICTION - MAX_FRICTION) * friction_factor
                mario_state.vx *= friction

        return context
