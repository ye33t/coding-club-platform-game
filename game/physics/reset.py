"""Detect when death animation is complete and trigger reset."""

from .base import PhysicsContext, PhysicsProcessor

# How far below screen Mario must fall before reset
RESET_THRESHOLD_Y = -200.0


class ResetProcessor(PhysicsProcessor):
    """Detects when death animation is complete and triggers reset.

    This processor:
    - Checks if dying Mario has fallen far enough
    - Sets should_reset flag when threshold reached
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check if reset should be triggered."""
        state = context.state

        # Only check if currently dying
        if not state.is_dying:
            return context

        # Check if Mario has fallen far enough to reset
        if state.y < RESET_THRESHOLD_Y:
            state.should_reset = True

        return context
