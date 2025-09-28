"""Update position based on velocity."""

from .base import PhysicsContext, PhysicsProcessor


class VelocityProcessor(PhysicsProcessor):
    """Updates position based on current velocity.

    This processor:
    - Applies velocity to position using delta time
    - Handles sub-pixel movement
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Update position from velocity."""
        mario_state = context.mario_state
        dt = context.dt

        # Update position based on velocity and delta time
        mario_state.x += mario_state.vx * dt
        mario_state.y += mario_state.vy * dt

        return context
