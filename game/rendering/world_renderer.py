"""Renderer responsible for drawing the world layers."""

from __future__ import annotations

from itertools import tee
from typing import TYPE_CHECKING

from ..constants import TILE_SIZE
from ..content import sprites
from .base import Renderer

if TYPE_CHECKING:
    from pygame import Surface

    from ..game import Game
    from ..world import World


class WorldRenderer(Renderer):
    """Draws world terrain, entities, and Mario in z-index order."""

    def __init__(self, world: "World"):
        self._world = world

    def draw(self, surface: "Surface", game: "Game") -> None:
        """Render background, dynamic entities, and terrain."""
        self._draw_background(surface)

        # Split drawables into behind/in front buckets lazily
        drawables_iter = self._world.drawables
        behind_iter, front_iter = tee(drawables_iter, 2)

        behind = sorted(
            (d for d in behind_iter if d.z_index < 0), key=lambda d: d.z_index
        )
        front = sorted(
            (d for d in front_iter if d.z_index >= 0), key=lambda d: d.z_index
        )

        for drawable in behind:
            drawable.draw(surface, self._world.camera)

        self._draw_terrain(surface)

        for drawable in front:
            drawable.draw(surface, self._world.camera)

    def _draw_background(self, surface: "Surface") -> None:
        """Draw the visible background tiles."""
        visible_tiles = self._world.level.get_visible_background_tiles(
            self._world.mario.screen, self._world.camera.x
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            tile_def = self._world.level.get_tile_definition(tile_type)
            if not tile_def or not tile_def.sprite_name:
                continue

            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            screen_x, screen_y = self._world.camera.world_to_screen(
                world_x, world_y
            )

            sprites.draw_at_position(
                surface,
                tile_def.sprite_sheet,
                tile_def.sprite_name,
                int(screen_x),
                int(screen_y),
            )

    def _draw_terrain(self, surface: "Surface") -> None:
        """Draw the visible terrain tiles."""
        visible_tiles = self._world.level.get_visible_terrain_tiles(
            self._world.mario.screen, self._world.camera.x
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            tile_def = self._world.level.get_tile_definition(tile_type)
            if not tile_def or not tile_def.sprite_name:
                continue

            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            visual = self._world.level.get_terrain_tile_visual_state(
                self._world.mario.screen, tile_x, tile_y
            )
            if visual:
                world_y += visual.offset_y

            screen_x, screen_y = self._world.camera.world_to_screen(
                world_x, world_y
            )

            sprites.draw_at_position(
                surface,
                tile_def.sprite_sheet,
                tile_def.sprite_name,
                int(screen_x),
                int(screen_y),
            )
