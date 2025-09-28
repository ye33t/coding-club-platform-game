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
        mario_state = context.mario_state

        # Clear skidding if velocity is low
        if mario_state.action == "skidding" and abs(mario_state.vx) < 10:
            mario_state.action = ""  # Clear action, will be re-determined

        # Only update action if not skidding
        if mario_state.action != "skidding":
            mario_state.action = self._determine_action(mario_state)

        return context

    def _determine_action(self, mario_state) -> str:
        """Determine Mario's action based on his physics state."""
        if mario_state.is_dying:
            return "dying"
        elif not mario_state.on_ground:
            return "jumping"
        elif abs(mario_state.vx) > RUN_THRESHOLD:
            return "running"
        elif abs(mario_state.vx) > 1.0:
            return "walking"
        else:
            return "idle"
