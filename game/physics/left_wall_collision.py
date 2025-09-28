"""Handle left wall collision detection and resolution."""

from ..collision_shapes import TileCollision
from ..constants import TILE_SIZE
from ..level import TILE_SLOPE_DOWN, TILE_SLOPE_UP
from .base import PhysicsContext, PhysicsProcessor


class LeftWallCollisionProcessor(PhysicsProcessor):
    """Handles left wall collision detection and resolution.

    This processor:
    - Detects collision with walls on the left side
    - Stops leftward movement into walls
    - Pushes Mario out to the right
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve left wall collisions."""
        state = context.mario
        level = context.level

        # Skip collision detection if dying
        if state.is_dying:
            return context

        # Only check if moving left
        if state.vx >= 0:
            return context

        # Sample points along Mario's left edge
        left_x = state.x

        # Check at multiple heights (bottom, middle, top)
        # Skip the very bottom to allow walking up single-pixel steps
        sample_heights = [
            state.y + 2,  # Near bottom (with 2 pixel tolerance)
            state.y + state.height / 2,  # Middle
            state.y + state.height - 2,  # Near top
        ]

        for sample_y in sample_heights:
            tile_x = int(left_x // TILE_SIZE)
            tile_y = int(sample_y // TILE_SIZE)

            tile_type = level.get_tile(tile_x, tile_y)

            # Skip slopes - they're handled by ground collision
            if tile_type in [TILE_SLOPE_UP, TILE_SLOPE_DOWN]:
                continue

            if tile_type != 0 and level.is_solid(tile_type):
                # Check if this is actually a wall at this height
                x_offset = left_x - (tile_x * TILE_SIZE)
                y_offset = sample_y - (tile_y * TILE_SIZE)

                # For regular tiles, always solid
                if TileCollision.is_solid_at(tile_type, x_offset, y_offset):
                    # Hit a wall on the left
                    # Push Mario to the right edge of the tile
                    state.x = (tile_x + 1) * TILE_SIZE
                    state.vx = 0  # Stop horizontal movement
                    break

        return context
