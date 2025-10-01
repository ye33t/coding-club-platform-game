"""Handle right wall collision detection and resolution."""

from ..constants import TILE_SIZE
from ..tile_definitions import is_quadrant_solid
from .base import PhysicsContext, PhysicsProcessor


class RightWallCollisionProcessor(PhysicsProcessor):
    """Handles right wall collision detection and resolution.

    This processor:
    - Detects collision with walls on the right side using quadrant masks
    - Stops rightward movement into walls
    - Pushes Mario out to the left
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve right wall collisions using quadrant masks."""
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

            tile_type = level.get_tile(mario_state.screen, tile_x, tile_y)
            tile_def = level.get_tile_definition(tile_type)

            if not tile_def or tile_def["collision_mask"] == 0:
                continue

            # Determine which quadrant we're checking
            x_in_tile = right_x - (tile_x * TILE_SIZE)
            y_in_tile = sample_y - (tile_y * TILE_SIZE)

            quadrant_x = 0 if x_in_tile < (TILE_SIZE / 2) else 1
            quadrant_y = 0 if y_in_tile < (TILE_SIZE / 2) else 1

            # Check if this quadrant is solid
            if is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
                # Hit a wall on the right
                # Push Mario to the left edge of the tile
                mario_state.x = (tile_x * TILE_SIZE) - mario_state.width
                mario_state.vx = 0  # Stop horizontal movement
                break

        return context
