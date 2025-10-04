"""Detect when death animation is complete and trigger reset."""

from ..camera import CameraState
from ..mario import MarioState
from .base import PhysicsContext, PhysicsProcessor
from .config import RESET_THRESHOLD_Y


class ResetProcessor(PhysicsProcessor):
    """Detects when death animation is complete and resets the game state.

    This processor:
    - Checks if dying Mario has fallen far enough
    - Resets Mario to starting position
    - Resets camera to origin
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check if reset should be triggered and perform reset."""
        state = context.mario_state

        # Only check if currently dying
        if not state.is_dying:
            return context

        # Check if Mario has fallen far enough to reset
        if state.y < RESET_THRESHOLD_Y:
            # Reset Mario to level's spawn position
            context.mario_state = MarioState(
                x=context.level.spawn_x,
                y=context.level.spawn_y,
                screen=context.level.spawn_screen,
            )
            # Reset camera to beginning (both position and ratchet)
            context.camera_state = CameraState(x=0, max_x=0)

        return context
