"""Rendering layers for world background, terrain, and entities."""

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


class BackgroundDrawablesLayer(RenderLayer):
    """Draws drawables positioned behind terrain."""

    def __init__(self, world: "World") -> None:
        self._world = world

    def draw(
        self,
        surface: "Surface",
        game: "Game",
        context: RenderContext,
    ) -> None:
        for drawable in context.behind_drawables:
            drawable.draw(surface, self._world.camera)


class TerrainLayer(RenderLayer):
    """Draws terrain tiles with any behavior-driven offsets."""

    def __init__(self, world: "World") -> None:
        self._world = world

    def draw(
        self,
        surface: "Surface",
        game: "Game",
        context: RenderContext,
    ) -> None:
        visible_tiles = self._world.level.get_visible_terrain_tiles(
            self._world.mario.screen,
            self._world.camera.x,
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            tile_def = self._world.level.get_tile_definition(tile_type)
            if not tile_def or not tile_def.sprite_name:
                continue

            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            visual = self._world.level.get_terrain_tile_visual_state(
                self._world.mario.screen,
                tile_x,
                tile_y,
            )
            if visual:
                world_y += visual.offset_y

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


class ForegroundDrawablesLayer(RenderLayer):
    """Draws drawables positioned at or above terrain."""

    def __init__(self, world: "World") -> None:
        self._world = world

    def draw(
        self,
        surface: "Surface",
        game: "Game",
        context: RenderContext,
    ) -> None:
        for drawable in context.front_drawables:
            drawable.draw(surface, self._world.camera)
