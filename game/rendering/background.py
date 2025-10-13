"""Render layer for drawing static background tiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import TILE_SIZE
from ..content import sprites
from .base import RenderContext, RenderLayer

if TYPE_CHECKING:
    from pygame import Surface

    from ..game import Game
    from ..world import World


class BackgroundLayer(RenderLayer):
    """Draws static background tiles."""

    def __init__(self, world: "World") -> None:
        self._world = world

    def draw(
        self,
        surface: "Surface",
        game: "Game",
        context: RenderContext,
    ) -> None:
        visible_tiles = self._world.level.get_visible_background_tiles(
            self._world.mario.screen,
            self._world.camera.x,
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            tile_def = self._world.level.get_tile_definition(tile_type)
            if not tile_def or not tile_def.sprite_name:
                continue

            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            screen_x, screen_y = self._world.camera.world_to_screen(
                world_x,
                world_y,
            )

            sprites.draw_at_position(
                surface,
                tile_def.sprite_sheet,
                tile_def.sprite_name,
                int(screen_x),
                int(screen_y),
            )
