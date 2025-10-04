"""Process player intent into target velocities and states."""

from .base import PhysicsContext, PhysicsProcessor
from .config import (
    AIR_ACCELERATION,
    GROUND_ACCELERATION,
    RUN_SPEED,
    SKID_DECELERATION,
    SKID_THRESHOLD,
    WALK_SPEED,
)


class IntentProcessor(PhysicsProcessor):
    """Converts player intent into target velocities and facing direction.

    This processor reads the player's intent and converts it into:
    - Target horizontal velocity
    - Facing direction
    - Skidding detection
    - Jump initiation
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process player intent."""
        mario_state = context.mario_state
        intent = context.mario_intent

        # Ignore all input if dying
        if mario_state.is_dying:
            return context

        # Calculate target horizontal velocity based on intent
        target_vx = 0.0

        if intent.move_right:
            target_vx = RUN_SPEED if intent.run else WALK_SPEED

            # Check for skidding (trying to reverse direction quickly)
            if mario_state.vx < -SKID_THRESHOLD and mario_state.on_ground:
                mario_state.action = "skidding"
            elif mario_state.action != "skidding":
                mario_state.facing_right = True

        elif intent.move_left:
            target_vx = -(RUN_SPEED if intent.run else WALK_SPEED)

            # Check for skidding
            if mario_state.vx > SKID_THRESHOLD and mario_state.on_ground:
                mario_state.action = "skidding"
            elif mario_state.action != "skidding":
                mario_state.facing_right = False

        # Apply acceleration whenever there's input
        if target_vx != 0:
            # Choose acceleration based on state
            if mario_state.action == "skidding":
                # Stronger deceleration when skidding
                acceleration = SKID_DECELERATION * context.dt
            elif mario_state.on_ground:
                # Normal ground acceleration
                acceleration = GROUND_ACCELERATION * context.dt
            else:
                # Weaker air control
                acceleration = AIR_ACCELERATION * context.dt

            # Apply acceleration to move velocity toward target
            if target_vx > mario_state.vx:
                # Accelerating to the right
                mario_state.vx = min(target_vx, mario_state.vx + acceleration)
            elif target_vx < mario_state.vx:
                # Accelerating to the left (or decelerating)
                mario_state.vx = max(target_vx, mario_state.vx - acceleration)

        # Handle jump intent
        # Just mark if we should jump - GravityProcessor will handle it
        if intent.jump and mario_state.on_ground:
            # Set a flag that GravityProcessor will read
            # For now, we'll use the intent directly in GravityProcessor
            pass

        return context
