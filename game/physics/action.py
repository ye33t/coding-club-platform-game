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
        mario = context.mario

        # Clear skidding if:
        # 1. Velocity is low (stopped or nearly stopped)
        # 2. Mario has changed direction (velocity crosses zero)
        if mario.action == "skidding":
            velocity_is_low = abs(mario.vx) < SKID_CLEAR_VELOCITY

            # Check if Mario has crossed zero velocity
            # When this happens, update facing direction
            if abs(mario.vx) < STOP_VELOCITY:
                # Mario has essentially stopped - update facing based on intent
                if context.mario_intent.move_right:
                    mario.facing_right = True
                elif context.mario_intent.move_left:
                    mario.facing_right = False
                mario.action = ""  # Clear action, will be re-determined
            elif velocity_is_low:
                mario.action = ""  # Clear action, will be re-determined

        # Only update action if not skidding
        if mario.action != "skidding":
            mario.action = self._determine_action(mario, context.mario_intent)

        return context

    def _determine_action(self, mario, mario_intent) -> str:
        """Determine Mario's action based on his physics state (velocity-based)."""
        # If Mario is in stomp mode and not on ground, keep stomping action
        if mario.is_stomping and not mario.on_ground:
            return "stomping"

        # Clear stomping state when Mario lands
        if mario.is_stomping and mario.on_ground:
            mario.is_stomping = False

        if not mario.on_ground:
            return "jumping"
        # Animation based on actual velocity, not input
        # This ensures Mario animates even when sliding without input
        elif abs(mario.vx) > RUN_SPEED_THRESHOLD:
            return "running"
        elif abs(mario.vx) > WALK_THRESHOLD:
            return "walking"
        else:
            return "idle"
