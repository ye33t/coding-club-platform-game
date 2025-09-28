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
        state = context.state
        dt = context.dt

        # Update position based on velocity and delta time
        state.x += state.vx * dt
        state.y += state.vy * dt

        return context
