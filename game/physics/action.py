"""Determine Mario's action based on physics state."""

from .base import PhysicsContext, PhysicsProcessor

# Speed thresholds
RUN_SPEED = 128.0  # pixels per second
RUN_THRESHOLD = RUN_SPEED * 0.8  # 80% of run speed


class ActionProcessor(PhysicsProcessor):
    """Determines Mario's action based on his physics state.

    This processor:
    - Sets the action (idle, walking, running, jumping)
    - Handles skidding state transitions
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Determine action from state."""
        state = context.mario

        # Clear skidding if velocity is low
        if state.action == "skidding" and abs(state.vx) < 10:
            state.action = ""  # Clear action, will be re-determined

        # Only update action if not skidding
        if state.action != "skidding":
            state.action = self._determine_action(state)

        return context

    def _determine_action(self, state) -> str:
        """Determine Mario's action based on his physics state."""
        if state.is_dying:
            return "dying"
        elif not state.on_ground:
            return "jumping"
        elif abs(state.vx) > RUN_THRESHOLD:
            return "running"
        elif abs(state.vx) > 1.0:
            return "walking"
        else:
            return "idle"
