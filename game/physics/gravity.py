"""Handle gravity and jumping physics."""

from .base import PhysicsContext, PhysicsProcessor
from .constants import (
    GRAVITY,
    JUMP_CUT_MULTIPLIER,
    RUN_JUMP_VELOCITY,
    RUN_SPEED_THRESHOLD,
    WALK_JUMP_VELOCITY,
)


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
