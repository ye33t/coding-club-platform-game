"""Detect when death animation is complete and trigger reset."""

from ..camera import CameraState
from ..constants import NATIVE_HEIGHT
from ..mario import MarioState
from .base import PhysicsContext, PhysicsProcessor

# How far below screen Mario must fall before reset
RESET_THRESHOLD_Y = -200.0

# Starting position for Mario - spawn in air, gravity will drop him
MARIO_START_X = 50.0
MARIO_START_Y = NATIVE_HEIGHT / 2  # Halfway up screen


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
            # Reset Mario to starting position
            context.mario_state = MarioState(x=MARIO_START_X, y=MARIO_START_Y)
            # Reset camera to beginning (both position and ratchet)
            context.camera_state = CameraState(x=0, max_x=0)

        return context
