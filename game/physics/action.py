"""Determine Mario's action based on physics state."""

from .base import PhysicsContext, PhysicsProcessor
from .config import (
    RUN_SPEED_THRESHOLD,
    SKID_CLEAR_VELOCITY,
    STOP_VELOCITY,
    WALK_THRESHOLD,
)


class ActionProcessor(PhysicsProcessor):
    """Determines Mario's action based on his physics state.

    This processor:
    - Sets the action (idle, walking, running, jumping)
    - Handles skidding state transitions
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Determine action from state."""
        mario_state = context.mario_state

        # Clear skidding if:
        # 1. Velocity is low (stopped or nearly stopped)
        # 2. Mario has changed direction (velocity crosses zero)
        if mario_state.action == "skidding":
            velocity_is_low = abs(mario_state.vx) < SKID_CLEAR_VELOCITY

            # Check if Mario has crossed zero velocity
            # When this happens, update facing direction
            if abs(mario_state.vx) < STOP_VELOCITY:
                # Mario has essentially stopped - update facing based on intent
                if context.mario_intent.move_right:
                    mario_state.facing_right = True
                elif context.mario_intent.move_left:
                    mario_state.facing_right = False
                mario_state.action = ""  # Clear action, will be re-determined
            elif velocity_is_low:
                mario_state.action = ""  # Clear action, will be re-determined

        # Only update action if not skidding
        if mario_state.action != "skidding":
            mario_state.action = self._determine_action(
                mario_state, context.mario_intent
            )

        return context

    def _determine_action(self, mario_state, mario_intent) -> str:
        """Determine Mario's action based on his physics state (velocity-based)."""
        # If Mario is in stomp mode and not on ground, keep stomping action
        if mario_state.is_stomping and not mario_state.on_ground:
            return "stomping"

        # Clear stomping state when Mario lands
        if mario_state.is_stomping and mario_state.on_ground:
            mario_state.is_stomping = False

        if not mario_state.on_ground:
            return "jumping"
        # Animation based on actual velocity, not input
        # This ensures Mario animates even when sliding without input
        elif abs(mario_state.vx) > RUN_SPEED_THRESHOLD:
            return "running"
        elif abs(mario_state.vx) > WALK_THRESHOLD:
            return "walking"
        else:
            return "idle"
