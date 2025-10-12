"""Handle gravity and jumping physics."""

from .base import PhysicsContext, PhysicsProcessor
from .config import (
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
        mario = context.mario
        intent = mario.intent
        dt = context.dt

        # Handle jump initiation
        if intent.jump and mario.on_ground:
            # Determine jump velocity based on horizontal speed
            is_running = abs(mario.vx) > RUN_SPEED_THRESHOLD

            if is_running:
                mario.vy = RUN_JUMP_VELOCITY
            else:
                mario.vy = WALK_JUMP_VELOCITY

            mario.on_ground = False
            mario.is_jumping = True

        # Clear jumping flag when landing
        if mario.on_ground:
            mario.is_jumping = False

        # Apply gravity when not on ground
        if not mario.on_ground:
            # Jump cut: release jump early while rising to apply stronger gravity
            if mario.is_jumping and not intent.jump and mario.vy > 0:
                mario.vy -= GRAVITY * JUMP_CUT_MULTIPLIER * dt
            else:
                mario.vy -= GRAVITY * dt

        return context
