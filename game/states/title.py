"""Title screen state that waits for the player to start a new game."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..constants import BLACK, INITIAL_LIVES, NATIVE_HEIGHT, SUB_TILE_SIZE
from ..rendering.text import draw_centered_text
from .base import State

if TYPE_CHECKING:
    from ..game import Game
    from ..rendering.base import RenderContext


class TitleState(State):
    """Display the NEW GAME prompt and seed a fresh run on Enter."""

    def __init__(self) -> None:
        self._enter_held = False

    def on_enter(self, game: "Game") -> None:
        self._enter_held = False
        game.world.reset(preserve_progress=False)
        game.world.hud.set_lives(0)

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
        self._start_new_game(game)

    def draw_overlay(self, game: "Game", context: "RenderContext") -> None:
        surface = context.surface
        surface.fill(BLACK)
        # Slightly offset the line so it sits near screen center
        center_y = (NATIVE_HEIGHT // 2) + SUB_TILE_SIZE
        draw_centered_text(surface, "NEW GAME", center_y)

    def _start_new_game(self, game: "Game") -> None:
        hud = game.world.hud
        hud.set_lives(INITIAL_LIVES)
        game.world.reset(preserve_progress=False)

        from ..rendering import TransitionMode
        from .life_splash import LifeSplashState

        game.transition(
            LifeSplashState(preserve_progress=False),
            TransitionMode.FADE_IN,
        )


# Backwards compatibility for older imports
InitialState = TitleState
