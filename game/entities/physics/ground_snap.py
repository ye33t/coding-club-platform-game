"""Ground snapping processor for entity physics."""

from __future__ import annotations

from dataclasses import dataclass

from ...constants import TILE_SIZE
from ...content.tile_definitions import is_quadrant_solid
from .base import EntityPhysicsContext


@dataclass(slots=True)
class GroundSnapProcessor:
    """Snap the entity to solid ground and update on-ground state."""

    tolerance: float

    def process(self, context: EntityPhysicsContext) -> EntityPhysicsContext:
        state = context.state
        level = context.level

        highest_ground = -1.0
        found_ground = False

        sample_points = [
            state.x,
            state.x + state.width / 2,
            state.x + state.width - 1,
        ]

        for sample_x in sample_points:
            tile_x = int(sample_x // TILE_SIZE)
            base_tile_y = int(state.y // TILE_SIZE)

            for check_y in (base_tile_y, base_tile_y - 1):
                if check_y < 0:
                    continue

                tile_type = level.get_terrain_tile(state.screen, tile_x, check_y)
                tile_def = level.get_tile_definition(tile_type)

                if not tile_def or tile_def.collision_mask == 0:
                    continue

                x_in_tile = sample_x - (tile_x * TILE_SIZE)
                quadrant_x = 0 if x_in_tile < (TILE_SIZE / 2) else 1

                for quadrant_y in (0, 1):
                    if not is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
                        continue

                    quadrant_top_y = check_y * TILE_SIZE + (quadrant_y + 1) * (
                        TILE_SIZE / 2
                    )

                    if (
                        abs(state.y - quadrant_top_y) <= self.tolerance
                        or state.y < quadrant_top_y
                    ):
                        if state.y <= quadrant_top_y + 1:
                            found_ground = True
                            if highest_ground < 0 or quadrant_top_y > highest_ground:
                                highest_ground = quadrant_top_y

        if found_ground and state.vy <= 0:
            state.y = highest_ground
            state.vy = 0
            state.on_ground = True
        else:
            state.on_ground = False

        return context
