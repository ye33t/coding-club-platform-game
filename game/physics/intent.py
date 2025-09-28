"""Process player intent into target velocities and states."""

from .base import PhysicsContext, PhysicsProcessor

# Movement constants
WALK_SPEED = 64.0  # pixels per second
RUN_SPEED = 128.0  # pixels per second
SKID_THRESHOLD = 80.0  # speed difference that triggers skidding


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
        state = context.mario
        intent = context.mario_intent

        # Ignore all input if dying
        if state.is_dying:
            return context

        # Calculate target horizontal velocity based on intent
        target_vx = 0.0

        if intent.move_right:
            target_vx = RUN_SPEED if intent.run else WALK_SPEED

            # Check for skidding (trying to reverse direction quickly)
            if state.vx < -SKID_THRESHOLD and state.on_ground:
                state.action = "skidding"
            else:
                state.facing_right = True

        elif intent.move_left:
            target_vx = -(RUN_SPEED if intent.run else WALK_SPEED)

            # Check for skidding
            if state.vx > SKID_THRESHOLD and state.on_ground:
                state.action = "skidding"
            else:
                state.facing_right = False

        # Store target velocity for the movement processor
        # Using a simple approach: directly set velocity
        # A more sophisticated approach would use acceleration
        if target_vx != 0:
            state.vx = target_vx

        # Handle jump intent
        # Just mark if we should jump - GravityProcessor will handle it
        if intent.jump and state.on_ground:
            # Set a flag that GravityProcessor will read
            # For now, we'll use the intent directly in GravityProcessor
            pass

        return context
