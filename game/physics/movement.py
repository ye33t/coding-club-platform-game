"""Handle movement physics including friction and deceleration."""

from .base import PhysicsContext, PhysicsProcessor

# Friction varies by speed for natural feel
MIN_FRICTION = 0.88  # At high speeds (more sliding)
MAX_FRICTION = 0.60  # At low speeds (quick stops)
FRICTION_SPEED_RANGE = 80.0  # Speed range over which friction varies


class MovementProcessor(PhysicsProcessor):
    """Handles horizontal movement physics.

    This processor manages:
    - Velocity-based friction for natural deceleration
    - Quick stops at low speeds, sliding at high speeds
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process movement physics."""
        mario_state = context.mario_state
        intent = context.mario_intent

        # Skip movement processing if dying
        if mario_state.is_dying:
            return context

        # If no horizontal movement intent, apply velocity-based friction
        if not intent.move_left and not intent.move_right:
            speed = abs(mario_state.vx)

            # Calculate friction based on speed
            # At 0 speed: MAX_FRICTION (0.60 = quick stop)
            # At FRICTION_SPEED_RANGE+: MIN_FRICTION (0.88 = more sliding)
            friction_factor = min(speed / FRICTION_SPEED_RANGE, 1.0)
            friction = MAX_FRICTION + (MIN_FRICTION - MAX_FRICTION) * friction_factor

            mario_state.vx *= friction

            # Stop completely if velocity is negligible (for numerical stability)
            if abs(mario_state.vx) < 1.0:
                mario_state.vx = 0.0

        return context
