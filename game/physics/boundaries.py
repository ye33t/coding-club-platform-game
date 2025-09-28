"""Enforce world boundaries."""

from .base import PhysicsContext, PhysicsProcessor


class BoundaryProcessor(PhysicsProcessor):
    """Enforces world boundaries.

    This processor:
    - Prevents Mario from going left of camera (ratcheting)
    - Prevents Mario from going past level edges
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Enforce boundaries."""
        state = context.state
        camera = context.camera
        level = context.level

        # Skip boundary enforcement if dying (allow falling off screen)
        if state.is_dying:
            return context

        # Mario can't go left of the camera position (ratcheting)
        if state.x < camera.x:
            state.x = camera.x
            state.vx = 0

        # Mario can't go past the right edge of the level
        if state.x > level.width_pixels - state.width:
            state.x = level.width_pixels - state.width
            state.vx = 0

        return context
