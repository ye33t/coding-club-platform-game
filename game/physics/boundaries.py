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
        mario = context.mario
        camera = context.camera
        level = context.level

        # Mario can't go left of the camera position (ratcheting)
        if mario.x < camera.x:
            mario.x = camera.x
            mario.vx = 0

        # Mario can't go past the right edge of the level
        if mario.x > level.width_pixels - mario.width:
            mario.x = level.width_pixels - mario.width
            mario.vx = 0

        return context
