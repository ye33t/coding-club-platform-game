"""Handle right wall collision detection and resolution."""

from ..collision_shapes import TileCollision
from ..constants import TILE_SIZE
from ..level import TILE_SLOPE_DOWN, TILE_SLOPE_UP
from .base import PhysicsContext, PhysicsProcessor


class RightWallCollisionProcessor(PhysicsProcessor):
    """Handles right wall collision detection and resolution.

    This processor:
    - Detects collision with walls on the right side
    - Stops rightward movement into walls
    - Pushes Mario out to the left
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve right wall collisions."""
        mario_state = context.mario_state
        level = context.level

        # Skip collision detection if dying
        if mario_state.is_dying:
            return context

        # Only check if moving right
        if mario_state.vx <= 0:
            return context

        # Sample points along Mario's right edge
        right_x = mario_state.x + mario_state.width - 1

        # Check at multiple heights (bottom, middle, top)
        # Skip the very bottom to allow walking up single-pixel steps
        sample_heights = [
            mario_state.y + 2,  # Near bottom (with 2 pixel tolerance)
            mario_state.y + mario_state.height / 2,  # Middle
            mario_state.y + mario_state.height - 2,  # Near top
        ]

        for sample_y in sample_heights:
            tile_x = int(right_x // TILE_SIZE)
            tile_y = int(sample_y // TILE_SIZE)

            tile_type = level.get_tile(tile_x, tile_y)

            # Skip slopes - they're handled by ground collision
            if tile_type in [TILE_SLOPE_UP, TILE_SLOPE_DOWN]:
                continue

            if tile_type != 0 and level.is_solid(tile_type):
                # Check if this is actually a wall at this height
                x_offset = right_x - (tile_x * TILE_SIZE)
                y_offset = sample_y - (tile_y * TILE_SIZE)

                # For regular tiles, always solid
                if TileCollision.is_solid_at(tile_type, x_offset, y_offset):
                    # Hit a wall on the right
                    # Push Mario to the left edge of the tile
                    mario_state.x = (tile_x * TILE_SIZE) - mario_state.width
                    mario_state.vx = 0  # Stop horizontal movement
                    break

        return context
