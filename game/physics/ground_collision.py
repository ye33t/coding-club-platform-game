"""Handle ground collision detection and resolution."""

from ..constants import TILE_SIZE
from ..tile_definitions import is_quadrant_solid
from .base import PhysicsContext, PhysicsProcessor


class GroundCollisionProcessor(PhysicsProcessor):
    """Handles ground collision detection and resolution.

    This processor:
    - Detects ground beneath Mario using quadrant-based collision
    - Sets on_ground flag
    - Snaps Mario to ground surface
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve ground collisions using quadrant masks."""
        mario_state = context.mario_state
        level = context.level

        # Skip collision detection if dying
        if mario_state.is_dying:
            return context

        highest_ground = -1.0  # Start with invalid value
        found_ground = False

        # Sample at left edge, center, and right edge of Mario's feet
        sample_points = [
            mario_state.x,
            mario_state.x + mario_state.width / 2,
            mario_state.x + mario_state.width - 1,
        ]

        for sample_x in sample_points:
            # Get tile coordinates (each tile is 16x16 pixels)
            tile_x = int(sample_x // TILE_SIZE)
            base_tile_y = int(mario_state.y // TILE_SIZE)

            # Check the tile Mario is in and one below
            for check_y in [base_tile_y, base_tile_y - 1]:
                if check_y < 0 or check_y >= level.height_tiles:
                    continue

                tile_type = level.get_tile(mario_state.screen, tile_x, check_y)
                tile_def = level.get_tile_definition(tile_type)

                if not tile_def or tile_def["collision_mask"] == 0:
                    continue

                # Each tile has 4 quadrants (8x8 pixels each)
                # Check which quadrant of the tile we're sampling
                x_in_tile = sample_x - (tile_x * TILE_SIZE)
                quadrant_x = 0 if x_in_tile < (TILE_SIZE / 2) else 1

                # Check both top and bottom quadrants
                for quadrant_y in [0, 1]:  # 0=bottom, 1=top
                    if not is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
                        continue

                    # Calculate world Y of this quadrant's top edge
                    quadrant_top_y = check_y * TILE_SIZE + (quadrant_y + 1) * (
                        TILE_SIZE / 2
                    )

                    # Check if Mario's feet are within collision range
                    if (
                        abs(mario_state.y - quadrant_top_y) <= 2.0
                        or mario_state.y < quadrant_top_y
                    ):
                        if mario_state.y <= quadrant_top_y + 1:
                            found_ground = True
                            if highest_ground < 0 or quadrant_top_y > highest_ground:
                                highest_ground = quadrant_top_y

        # Apply ground collision
        if found_ground and mario_state.vy <= 0:
            mario_state.y = highest_ground
            mario_state.vy = 0
            mario_state.on_ground = True
        else:
            mario_state.on_ground = False

        return context
