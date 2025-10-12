"""Handle ceiling collision detection and resolution."""

from ..constants import TILE_SIZE
from ..content.tile_definitions import is_quadrant_solid
from ..terrain.base import TileEvent
from .base import PhysicsContext, PhysicsProcessor
from .config import CEILING_BOUNCE_VELOCITY, CEILING_SAMPLE_EDGE_OFFSET


class CeilingCollisionProcessor(PhysicsProcessor):
    """Handles ceiling collision detection and resolution.

    This processor:
    - Detects when Mario's head hits a ceiling using quadrant masks
    - Applies small downward bounce velocity
    - Pushes Mario down flush with ceiling (no penetration)
    """

    def process(self, context: PhysicsContext) -> PhysicsContext:
        """Check and resolve ceiling collisions using quadrant masks."""
        mario = context.mario
        level = context.level

        # Only check ceiling if moving upward
        if mario.vy <= 0:
            return context

        # Check Mario's head position (top of hitbox)
        head_y = mario.y + mario.height

        # Sample points across Mario's width for ceiling
        ceiling_sample_points = [
            mario.x + CEILING_SAMPLE_EDGE_OFFSET,  # Slightly inset to avoid edge issues
            mario.x + mario.width / 2,
            mario.x + mario.width - CEILING_SAMPLE_EDGE_OFFSET - 1,
        ]

        for sample_x in ceiling_sample_points:
            tile_x = int(sample_x // TILE_SIZE)
            tile_y = int(head_y // TILE_SIZE)

            tile_type = level.get_terrain_tile(mario.screen, tile_x, tile_y)
            tile_def = level.get_tile_definition(tile_type)

            if not tile_def or tile_def.collision_mask == 0:
                continue

            # Determine which quadrant we're checking
            x_in_tile = sample_x - (tile_x * TILE_SIZE)
            y_in_tile = head_y - (tile_y * TILE_SIZE)

            quadrant_x = 0 if x_in_tile < (TILE_SIZE / 2) else 1
            quadrant_y = 0 if y_in_tile < (TILE_SIZE / 2) else 1

            # Check if this quadrant is solid
            if is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
                # Mario's head hit a ceiling - push him down flush with block
                mario.y = (tile_y * TILE_SIZE) - mario.height
                # Apply small downward bounce velocity
                mario.vy = CEILING_BOUNCE_VELOCITY

                # Trigger bounce behavior on the tile
                context.level.terrain_manager.trigger_event(
                    mario.screen, tile_x, tile_y, TileEvent.HIT_FROM_BELOW
                )
                break

        return context
