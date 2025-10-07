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
        mario_state = context.mario_state
        camera_state = context.camera_state
        level = context.level

        # Mario can't go left of the camera position (ratcheting)
        if mario_state.x < camera_state.x:
            mario_state.x = camera_state.x
            mario_state.vx = 0

        # Mario can't go past the right edge of the level
        if mario_state.x > level.width_pixels - mario_state.width:
            mario_state.x = level.width_pixels - mario_state.width
            mario_state.vx = 0

        return context
