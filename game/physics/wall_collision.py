"""Handle wall collision detection and resolution for both directions."""

from enum import Enum

from ..constants import TILE_SIZE
from ..tile_definitions import is_quadrant_solid
from .base import PhysicsContext, PhysicsProcessor
from .config import WALL_DEAD_ZONE, WALL_SAMPLE_TOP_OFFSET


class Direction(Enum):
    """Wall collision direction."""

    LEFT = "left"
    RIGHT = "right"


class WallCollisionProcessor(PhysicsProcessor):
    """Handles wall collision detection and resolution for both sides.

    This processor:
    - Detects collision with walls using quadrant masks
    - Stops movement into walls
    - Pushes Mario out of walls
    """

    def __init__(self, direction: Direction):
        """Initialize with collision direction.

        Args:
            direction: Which side to check (LEFT or RIGHT)
        """
        self.direction = direction

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve wall collisions using quadrant masks."""
        mario_state = context.mario_state
        level = context.level

        # Only check if moving in the appropriate direction
        if self.direction == Direction.LEFT and mario_state.vx >= 0:
            return context
        if self.direction == Direction.RIGHT and mario_state.vx <= 0:
            return context

        # Calculate edge position based on direction
        if self.direction == Direction.LEFT:
            edge_x = mario_state.x
        else:  # RIGHT
            edge_x = mario_state.x + mario_state.width - 1

        # Check at multiple heights (bottom, middle, top)
        # Skip the very bottom to avoid collision with ground tiles
        sample_heights = [
            mario_state.y + WALL_DEAD_ZONE,  # Above feet (tolerance for ground)
            mario_state.y + mario_state.height / 2,  # Middle
            mario_state.y + mario_state.height - WALL_SAMPLE_TOP_OFFSET,  # Near top
        ]

        for sample_y in sample_heights:
            tile_x = int(edge_x // TILE_SIZE)
            tile_y = int(sample_y // TILE_SIZE)

            tile_type = level.get_tile(mario_state.screen, tile_x, tile_y)
            tile_def = level.get_tile_definition(tile_type)

            if not tile_def or tile_def["collision_mask"] == 0:
                continue

            # Determine which quadrant we're checking
            x_in_tile = edge_x - (tile_x * TILE_SIZE)
            y_in_tile = sample_y - (tile_y * TILE_SIZE)

            quadrant_x = 0 if x_in_tile < (TILE_SIZE / 2) else 1
            quadrant_y = 0 if y_in_tile < (TILE_SIZE / 2) else 1

            # Check if this quadrant is solid
            if is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
                # Hit a wall - push Mario out
                if self.direction == Direction.LEFT:
                    # Push to the right edge of the tile
                    mario_state.x = (tile_x + 1) * TILE_SIZE
                else:  # RIGHT
                    # Push to the left edge of the tile
                    mario_state.x = (tile_x * TILE_SIZE) - mario_state.width

                mario_state.vx = 0  # Stop horizontal movement
                break

        return context
