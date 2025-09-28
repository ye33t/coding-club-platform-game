"""Handle ceiling collision detection and resolution."""

from ..constants import TILE_SIZE
from .base import PhysicsContext, PhysicsProcessor

PENETRATION_ALLOWANCE = TILE_SIZE // 2  # Allow slight penetration for better feel


class CeilingCollisionProcessor(PhysicsProcessor):
    """Handles ceiling collision detection and resolution.

    This processor:
    - Detects when Mario's head hits a ceiling
    - Stops upward movement
    - Pushes Mario down to valid position
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve ceiling collisions."""
        state = context.state
        level = context.level

        # Skip collision detection if dying
        if state.is_dying:
            return context

        # Only check ceiling if moving upward
        if state.vy <= 0:
            return context

        # Allow a few pixels of penetration for better game feel
        head_y = state.y + state.height - PENETRATION_ALLOWANCE

        # Sample points across Mario's width for ceiling
        ceiling_sample_points = [
            state.x + 1,  # Slightly inset to avoid edge issues
            state.x + state.width / 2,
            state.x + state.width - 2,
        ]

        for sample_x in ceiling_sample_points:
            tile_x = int(sample_x // TILE_SIZE)
            tile_y = int(head_y // TILE_SIZE)

            tile_type = level.get_tile(tile_x, tile_y)
            if tile_type != 0 and level.is_solid(tile_type):
                # Mario's head penetrated into a solid tile
                # Push him back down but allow slight penetration for better feel
                state.y = (tile_y * TILE_SIZE) - state.height + PENETRATION_ALLOWANCE
                state.vy = 0  # Stop upward movement
                break

        return context
