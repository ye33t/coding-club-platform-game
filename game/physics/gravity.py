"""Handle gravity and jumping physics."""

from .base import PhysicsContext, PhysicsProcessor

GRAVITY = 400.0  # pixels per second squared
JUMP_VELOCITY = 200.0  # pixels per second


class GravityProcessor(PhysicsProcessor):
    """Handles vertical physics.

    This processor manages:
    - Gravity application
    - Jump initiation
    - Terminal velocity (future)
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process gravity and jumping."""
        state = context.state
        intent = context.intent
        dt = context.dt

        # Skip normal gravity if dying (DeathPhysicsProcessor handles it)
        if state.is_dying:
            return context

        # Handle jump initiation
        if intent.jump and state.on_ground:
            state.vy = JUMP_VELOCITY
            state.on_ground = False

        # Apply gravity when not on ground
        if not state.on_ground:
            state.vy -= GRAVITY * dt

        return context
