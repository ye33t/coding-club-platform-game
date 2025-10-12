"""Handle movement physics including friction and deceleration."""

from .base import PhysicsContext, PhysicsProcessor
from .config import FRICTION_SPEED_RANGE, MAX_FRICTION, MIN_FRICTION, STOP_THRESHOLD


class MovementProcessor(PhysicsProcessor):
    """Handles horizontal movement physics.

    This processor manages:
    - Speed-based friction for natural deceleration
    - More friction at low speeds (walking), less at high speeds (running)
    - Instant stop below threshold
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process movement physics."""
        mario = context.mario
        intent = context.mario_intent

        # If no horizontal movement intent, apply friction
        if not intent.move_left and not intent.move_right:
            speed = abs(mario.vx)

            # Below threshold: instant stop
            if speed < STOP_THRESHOLD:
                mario.vx = 0.0
            else:
                # Speed-based friction:
                # At low speeds (walking): MAX_FRICTION (more friction, less slide)
                # At high speeds (running): MIN_FRICTION (less friction, more slide)
                friction_factor = min(speed / FRICTION_SPEED_RANGE, 1.0)
                friction = (
                    MAX_FRICTION + (MIN_FRICTION - MAX_FRICTION) * friction_factor
                )
                mario.vx *= friction

        return context
