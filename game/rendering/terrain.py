"""Render layer for drawing terrain tiles with behavior offsets."""

from __future__ import annotations

from ..constants import TILE_SIZE
from ..content import sprites
from .base import RenderContext, RenderLayer


class TerrainLayer(RenderLayer):
    """Draws terrain tiles with any behavior-driven offsets."""

    def draw(
        self,
        context: RenderContext,
    ) -> None:
        visible_tiles = context.level.get_visible_terrain_tiles(
            context.mario.screen,
            context.camera.x,
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            tile_def = context.level.get_tile_definition(tile_type)
            if not tile_def or not tile_def.sprite_name:
                continue

            world_x: float = tile_x * TILE_SIZE
            world_y: float = tile_y * TILE_SIZE

            visual = context.level.get_terrain_tile_visual_state(
                context.mario.screen,
                tile_x,
                tile_y,
            )
            if visual:
                world_y += visual.offset_y

            screen_x, screen_y = context.camera.world_to_screen(
                world_x,
                world_y,
            )

            sprites.draw_at_position(
                context.surface,
                tile_def.sprite_sheet,
                tile_def.sprite_name,
                int(screen_x),
                int(screen_y),
            )
