"""Overlay layers such as transitions and debug visualization."""

from __future__ import annotations

import math
from enum import Enum
from typing import Callable, Optional, TYPE_CHECKING

import pygame

from ..constants import (
    BACKGROUND_COLOR,
    BLACK,
    NATIVE_HEIGHT,
    NATIVE_WIDTH,
    SUB_TILE_SIZE,
    WHITE,
)
from .base import RenderContext, RenderLayer

if TYPE_CHECKING:
    from pygame import Surface

    from ..game import Game


class TransitionMode(Enum):
    """Transition animation mode for scene changes."""

    INSTANT = "instant"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    BOTH = "both"


class TransitionLayer(RenderLayer):
    """Circular iris transition overlay."""

    def __init__(
        self,
        duration: float,
        mode: TransitionMode,
        on_midpoint: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        self._duration = duration
        self._mode = mode
        self._on_midpoint = on_midpoint
        self._on_complete = on_complete
        self._elapsed = 0.0
        self._midpoint_triggered = False
        self._completed = False

    def on_added(self, game: "Game") -> None:
        if self._mode == TransitionMode.FADE_IN and self._on_midpoint:
            self._on_midpoint()
            self._midpoint_triggered = True

    def update(self, dt: float, game: "Game") -> bool:
        if self._completed:
            return False

        self._elapsed += dt

        if not self._midpoint_triggered and self._on_midpoint:
            trigger = False
            if self._mode == TransitionMode.BOTH:
                trigger = self._elapsed >= self._duration / 2
            elif self._mode == TransitionMode.FADE_OUT:
                trigger = False

            if trigger:
                self._on_midpoint()
                self._midpoint_triggered = True

        if self._elapsed >= self._duration:
            if not self._midpoint_triggered and self._on_midpoint:
                # For FADE_OUT we do the state change at completion.
                self._on_midpoint()
                self._midpoint_triggered = True
            if self._on_complete:
                self._on_complete()
            self._completed = True
            return False

        return True

    def draw(
        self,
        surface: "Surface",
        game: "Game",
        context: RenderContext,
    ) -> None:
        progress = (
            1.0 if self._duration <= 0 else min(1.0, self._elapsed / self._duration)
        )
        max_radius = math.hypot(NATIVE_WIDTH / 2, NATIVE_HEIGHT / 2)

        if self._mode == TransitionMode.FADE_OUT:
            eased = progress * progress * (3 - 2 * progress)
            radius = max_radius * (1 - eased)
        elif self._mode == TransitionMode.FADE_IN:
            eased = progress * progress * (3 - 2 * progress)
            radius = max_radius * eased
        else:
            if progress < 0.5:
                local_progress = progress * 2
                eased = local_progress * local_progress * (3 - 2 * local_progress)
                radius = max_radius * (1 - eased)
            else:
                local_progress = (progress - 0.5) * 2
                eased = local_progress * local_progress * (3 - 2 * local_progress)
                radius = max_radius * eased

        mask = pygame.Surface((NATIVE_WIDTH, NATIVE_HEIGHT))
        mask.fill(BLACK)

        center = (NATIVE_WIDTH // 2, NATIVE_HEIGHT // 2)
        if radius > 0:
            pygame.draw.circle(mask, BACKGROUND_COLOR, center, int(radius))

        mask.set_colorkey(BACKGROUND_COLOR)
        surface.blit(mask, (0, 0))


class DebugOverlayLayer(RenderLayer):
    """Draws debug tile grid and textual diagnostics."""

    def update(self, dt: float, game: "Game") -> bool:
        return True

    def draw(
        self,
        surface: "Surface",
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
                pygame.draw.line(surface, (100, 100, 100), (int(x), 0), (int(x), height))
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
