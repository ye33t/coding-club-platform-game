"""Handle ceiling collision detection and resolution."""

from ..constants import BLOCK_SIZE
from ..tile_definitions import is_quadrant_solid
from .base import PhysicsContext, PhysicsProcessor

# Small downward velocity applied when hitting ceiling
CEILING_BOUNCE_VELOCITY = -20.0  # pixels per second


class CeilingCollisionProcessor(PhysicsProcessor):
    """Handles ceiling collision detection and resolution.

    This processor:
    - Detects when Mario's head hits a ceiling using quadrant masks
    - Applies small downward bounce velocity
    - Pushes Mario down flush with ceiling (no penetration)
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve ceiling collisions using quadrant masks."""
        mario_state = context.mario_state
        level = context.level

        # Skip collision detection if dying
        if mario_state.is_dying:
            return context

        # Only check ceiling if moving upward
        if mario_state.vy <= 0:
            return context

        # Check Mario's head position (top of hitbox)
        head_y = mario_state.y + mario_state.height

        # Sample points across Mario's width for ceiling
        ceiling_sample_points = [
            mario_state.x + 1,  # Slightly inset to avoid edge issues
            mario_state.x + mario_state.width / 2,
            mario_state.x + mario_state.width - 2,
        ]

        for sample_x in ceiling_sample_points:
            tile_x = int(sample_x // BLOCK_SIZE)
            tile_y = int(head_y // BLOCK_SIZE)

            tile_type = level.get_tile(tile_x, tile_y)
            tile_def = level.get_tile_definition(tile_type)

            if not tile_def or tile_def["collision_mask"] == 0:
                continue

            # Determine which quadrant we're checking
            x_in_tile = sample_x - (tile_x * BLOCK_SIZE)
            y_in_tile = head_y - (tile_y * BLOCK_SIZE)

            quadrant_x = 0 if x_in_tile < (BLOCK_SIZE / 2) else 1
            quadrant_y = 0 if y_in_tile < (BLOCK_SIZE / 2) else 1

            # Check if this quadrant is solid
            if is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
                # Mario's head hit a ceiling - push him down flush with block
                mario_state.y = (tile_y * BLOCK_SIZE) - mario_state.height
                # Apply small downward bounce velocity
                mario_state.vy = CEILING_BOUNCE_VELOCITY
                break

        return context
