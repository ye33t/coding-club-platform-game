"""Handle ground collision detection and resolution."""

from ..collision_shapes import TileCollision
from ..constants import TILE_SIZE
from .base import PhysicsContext, PhysicsProcessor


class GroundCollisionProcessor(PhysicsProcessor):
    """Handles ground collision detection and resolution.

    This processor:
    - Detects ground beneath Mario (including slopes)
    - Sets on_ground flag
    - Snaps Mario to ground surface
    - Handles slope physics
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve ground collisions including slopes."""
        state = context.mario
        level = context.level

        # Skip collision detection if dying
        if state.is_dying:
            return context

        highest_ground = -1.0  # Start with invalid value
        found_ground = False

        # Sample at left edge, center, and right edge
        sample_points = [
            state.x,
            state.x + state.width / 2,
            state.x + state.width - 1,
        ]

        for sample_x in sample_points:
            # Get tile coordinates
            tile_x = int(sample_x // TILE_SIZE)

            # Check tiles from 2 below to 1 above Mario's position
            # This ensures we catch slopes that extend into adjacent tiles
            base_tile_y = int(state.y // TILE_SIZE)

            for check_y in range(base_tile_y - 2, base_tile_y + 2):
                if check_y < 0 or check_y >= level.height_tiles:
                    continue

                tile_type = level.get_tile(tile_x, check_y)
                if tile_type != 0:
                    # Calculate position within tile
                    x_offset = sample_x - (tile_x * TILE_SIZE)

                    # Get ground height at this position
                    ground_height = TileCollision.get_ground_height(tile_type, x_offset)
                    if ground_height is not None:
                        # Convert to world coordinates
                        world_ground_y = check_y * TILE_SIZE + ground_height

                        # Check if Mario is within collision range of this ground
                        # Allow a small margin for floating point precision
                        if (
                            abs(state.y - world_ground_y) <= 2.0
                            or state.y < world_ground_y
                        ):
                            if state.y <= world_ground_y + 1:
                                found_ground = True
                                if (
                                    highest_ground < 0
                                    or world_ground_y > highest_ground
                                ):
                                    highest_ground = world_ground_y

        # Apply ground collision
        if found_ground and state.vy <= 0:
            state.y = highest_ground
            state.vy = 0
            state.on_ground = True
        else:
            state.on_ground = False

        return context
