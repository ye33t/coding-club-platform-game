"""Render layer for drawing static background tiles."""

from __future__ import annotations

from ..constants import TILE_SIZE
from ..content import sprites
from .base import RenderContext, RenderLayer


class BackgroundLayer(RenderLayer):
    """Draws static background tiles."""

    def draw(
        self,
        context: RenderContext,
    ) -> None:
        visible_tiles = context.level.get_visible_background_tiles(
            context.mario.screen,
            context.camera.x,
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            tile_def = context.level.get_tile_definition(tile_type)
            if not tile_def:
                continue

            sprite_name = tile_def.resolve_sprite_name(
                context.game.world.animation_tick
            )
            if not sprite_name:
                continue

            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            screen_x, screen_y = context.camera.world_to_screen(
                world_x,
                world_y,
            )

            sprites.draw_at_position(
                context.surface,
                tile_def.sprite_sheet,
                sprite_name,
                int(screen_x),
                int(screen_y),
                palette=context.palette_scheme_name,
            )
