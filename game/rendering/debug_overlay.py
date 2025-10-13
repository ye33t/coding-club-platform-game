"""Overlay layers such as transitions and debug visualization."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..constants import SUB_TILE_SIZE, WHITE
from .base import RenderContext, RenderLayer

if TYPE_CHECKING:
    from pygame import Surface

    from ..game import Game


class DebugOverlayLayer(RenderLayer):
    """Draws debug tile grid and textual diagnostics."""

    def update(self, dt: float, game: "Game") -> bool:
        return True

    def draw(
        self,
        surface: Surface,
        game: "Game",
        context: RenderContext,
    ) -> None:
        self._draw_tile_grid(surface, game)
        self._draw_debug_info(surface, game)

    def _draw_tile_grid(self, surface: "Surface", game: "Game") -> None:
        width = surface.get_width()
        height = surface.get_height()
        camera_x = game.world.camera.x

        offset_x = -(camera_x % SUB_TILE_SIZE)
        x = offset_x
        while x <= width:
            if x >= 0:
                pygame.draw.line(
                    surface, (100, 100, 100), (int(x), 0), (int(x), height)
                )
            x += SUB_TILE_SIZE

        y = 0
        while y <= height:
            pygame.draw.line(surface, (100, 100, 100), (0, int(y)), (width, int(y)))
            y += SUB_TILE_SIZE

    def _draw_debug_info(self, surface: "Surface", game: "Game") -> None:
        font = game.font
        if font is None:
            return

        fps = game.clock.get_fps()
        debug_lines = [
            f"FPS: {fps:.1f}",
            f"Resolution: {surface.get_width()}x{surface.get_height()}",
            f"Scale: {game.display.scale}x",
            f"Mario Pos: ({game.world.mario.x:.2f}, {game.world.mario.y:.2f})",
            f"Mario Vel: ({game.world.mario.vx:.2f}, {game.world.mario.vy:.2f})",
            f"Camera X: {game.world.camera.x:.2f}",
            f"Screen: {game.world.mario.screen}",
            f"Entities: {len(game.world.entities._entities)}",
        ]

        for i, line in enumerate(debug_lines):
            text_surface = font.render(line, True, WHITE)
            surface.blit(text_surface, (8, 8 + i * 12))
