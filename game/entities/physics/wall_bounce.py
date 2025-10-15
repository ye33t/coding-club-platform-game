"""Wall bounce processor for entity physics."""

from __future__ import annotations

from dataclasses import dataclass

from ...constants import TILE_SIZE
from ...content.tile_definitions import is_quadrant_solid
from .base import EntityPhysicsContext


@dataclass(slots=True)
class WallBounceProcessor:
    """Bounce the entity off solid tiles, reversing direction."""

    speed: float

    def process(self, context: EntityPhysicsContext) -> EntityPhysicsContext:
        state = context.state

        if state.vx == 0:
            return context

        level = context.level

        if state.vx > 0:
            edge_x = state.x + state.width - 1
        else:
            edge_x = state.x

        sample_y = state.y + (state.height / 2)

        tile_x = int(edge_x // TILE_SIZE)
        tile_y = int(sample_y // TILE_SIZE)

        tile_type = level.get_terrain_tile(state.screen, tile_x, tile_y)
        tile_def = level.get_tile_definition(tile_type)

        if not tile_def or tile_def.collision_mask == 0:
            return context

        x_in_tile = edge_x - (tile_x * TILE_SIZE)
        y_in_tile = sample_y - (tile_y * TILE_SIZE)

        quadrant_x = 0 if x_in_tile < (TILE_SIZE / 2) else 1
        quadrant_y = 0 if y_in_tile < (TILE_SIZE / 2) else 1

        if is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
            state.direction *= -1
            state.vx = self.speed * state.direction

            if state.direction > 0:
                state.x = (tile_x + 1) * TILE_SIZE
            else:
                state.x = (tile_x * TILE_SIZE) - state.width

        return context
