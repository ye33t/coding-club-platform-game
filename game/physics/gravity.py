"""Handle gravity and jumping physics."""

from .base import PhysicsContext, PhysicsProcessor

# Gravity constants
GRAVITY = 400.0  # pixels per second squared
JUMP_CUT_MULTIPLIER = 3.0  # Multiply gravity when jump button released early

# Jump velocities tuned for desired heights:
# - Walk jump: 4 blocks (64px) high
# - Run jump: 6 blocks (96px) high
WALK_JUMP_VELOCITY = 226.0  # pixels per second
RUN_JUMP_VELOCITY = 277.0  # pixels per second

# Speed threshold to determine if running
RUN_SPEED_THRESHOLD = 100.0  # pixels per second


class GravityProcessor(PhysicsProcessor):
    """Handles vertical physics.

    This processor manages:
    - Variable-height jumping (based on button hold and speed)
    - Gravity application with jump cut mechanic
    - Jump state tracking
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Process gravity and jumping with variable height."""
        mario_state = context.mario_state
        intent = context.mario_intent
        dt = context.dt

        # Skip normal gravity if dying (DeathPhysicsProcessor handles it)
        if mario_state.is_dying:
            return context

        # Handle jump initiation
        if intent.jump and mario_state.on_ground:
            # Determine jump velocity based on horizontal speed
            is_running = abs(mario_state.vx) > RUN_SPEED_THRESHOLD

            if is_running:
                mario_state.vy = RUN_JUMP_VELOCITY
            else:
                mario_state.vy = WALK_JUMP_VELOCITY

            mario_state.on_ground = False
            mario_state.is_jumping = True

        # Clear jumping flag when landing
        if mario_state.on_ground:
            mario_state.is_jumping = False

        # Apply gravity when not on ground
        if not mario_state.on_ground:
            # Jump cut: If button released early while moving upward, apply stronger gravity
            if mario_state.is_jumping and not intent.jump and mario_state.vy > 0:
                mario_state.vy -= GRAVITY * JUMP_CUT_MULTIPLIER * dt
            else:
                mario_state.vy -= GRAVITY * dt

        return context
