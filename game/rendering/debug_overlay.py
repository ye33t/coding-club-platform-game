"""Overlay layers such as transitions and debug visualization."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import Surface

from ..constants import SUB_TILE_SIZE, WHITE
from .base import RenderContext, RenderLayer

if TYPE_CHECKING:
    from ..game import Game


class DebugOverlayLayer(RenderLayer):
    """Draws debug tile grid and textual diagnostics."""

    def __init__(self) -> None:
        self._font = pygame.font.Font(None, 16)

    def draw(
        self,
        context: RenderContext,
    ) -> None:
        self._draw_tile_grid(context.surface, context.game)
        self._draw_debug_info(context.surface, context.game)

    def _draw_tile_grid(self, surface: Surface, game: Game) -> None:
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
        fps = game.clock.get_fps()
        debug_lines = [
            f"FPS: {fps:.1f}",
            f"Resolution: {surface.get_width()}x{surface.get_height()}",
            f"Mario Pos: ({game.world.mario.x:.2f}, {game.world.mario.y:.2f})",
            f"Mario Vel: ({game.world.mario.vx:.2f}, {game.world.mario.vy:.2f})",
            f"Camera X: {game.world.camera.x:.2f}",
            f"Screen: {game.world.mario.screen}",
            f"Entities: {len(game.world.entities._entities)}",
        ]

        for i, line in enumerate(debug_lines):
            text_surface = self._font.render(line, True, WHITE)
            surface.blit(text_surface, (8, 8 + i * 12))
