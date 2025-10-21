"""Game over screen when Mario runs out of lives."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..constants import BLACK, NATIVE_HEIGHT, SUB_TILE_SIZE
from ..rendering.text import draw_centered_text
from .base import State

if TYPE_CHECKING:
    from ..game import Game
    from ..rendering.base import RenderContext


class GameOverState(State):
    """Display GAME OVER and wait for the player to return to the title."""

    def __init__(self) -> None:
        self._enter_held = False

    def on_enter(self, game: "Game") -> None:
        self._enter_held = False
        game.world.reset(preserve_progress=False)

    def update(self, game: "Game", dt: float) -> None:
        if game.transitioning:
            return

        keys = pygame.key.get_pressed()
        pressed = keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]
        if not pressed:
            self._enter_held = False
            return

        if self._enter_held:
            return

        self._enter_held = True
        self._return_to_title(game)

    def draw_overlay(self, game: "Game", context: "RenderContext") -> None:
        surface = context.surface
        surface.fill(BLACK)
        center_y = (NATIVE_HEIGHT // 2) + SUB_TILE_SIZE
        draw_centered_text(surface, "GAME OVER", center_y)

    def _return_to_title(self, game: "Game") -> None:
        from ..rendering import TransitionMode
        from .title import TitleState

        game.transition(TitleState(), TransitionMode.INSTANT)
