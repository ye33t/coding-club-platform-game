"""Process player intent into target velocities and states."""

from .base import PhysicsContext, PhysicsProcessor

# Movement constants
WALK_SPEED = 64.0  # pixels per second
RUN_SPEED = 128.0  # pixels per second
SKID_THRESHOLD = 80.0  # speed difference that triggers skidding

# Acceleration constants (pixels per second²)
GROUND_ACCELERATION = 400.0  # Normal ground acceleration
SKID_DECELERATION = 600.0  # Deceleration when skidding (stronger)
AIR_ACCELERATION = 200.0  # Air control (weaker)


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

        # Track input duration for distinguishing taps from holds
        # Check if continuing in same direction
        continuing_same_direction = False

        if intent.move_right:
            target_vx = RUN_SPEED if intent.run else WALK_SPEED
            # Check if this continues previous input
            continuing_same_direction = (
                mario_state.facing_right and mario_state.vx >= -5.0
            )

            # Check for skidding (trying to reverse direction quickly)
            if mario_state.vx < -SKID_THRESHOLD and mario_state.on_ground:
                mario_state.action = "skidding"
                mario_state.input_duration = 0  # Reset on direction change
            elif mario_state.action != "skidding":
                mario_state.facing_right = True

        elif intent.move_left:
            target_vx = -(RUN_SPEED if intent.run else WALK_SPEED)
            # Check if this continues previous input
            continuing_same_direction = (
                not mario_state.facing_right and mario_state.vx <= 5.0
            )

            # Check for skidding
            if mario_state.vx > SKID_THRESHOLD and mario_state.on_ground:
                mario_state.action = "skidding"
                mario_state.input_duration = 0  # Reset on direction change
            elif mario_state.action != "skidding":
                mario_state.facing_right = False
        else:
            # No input - reset duration
            mario_state.input_duration = 0

        # Update input duration
        if target_vx != 0:
            if continuing_same_direction:
                mario_state.input_duration += 1
            else:
                mario_state.input_duration = 1  # First frame of new input

        # Only apply acceleration if:
        # - Input held for 3+ frames (not just a tap), OR
        # - Already moving significantly (keep momentum)
        nearly_stopped = abs(mario_state.vx) < 5.0
        if target_vx != 0 and (mario_state.input_duration >= 9 or not nearly_stopped):
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
