"""Inter-level splash that shows the current world and remaining lives."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import (
    BLACK,
    LIFE_SPLASH_FRAMES,
    NATIVE_HEIGHT,
    NATIVE_WIDTH,
    SUB_TILE_SIZE,
)
from ..content import sprites
from ..rendering.text import draw_centered_text, draw_text
from .base import State

if TYPE_CHECKING:
    from ..game import Game
    from ..rendering.base import RenderContext


class LifeSplashState(State):
    """Display world and life info for a brief pause before play."""

    def __init__(self, preserve_progress: bool) -> None:
        self._preserve_progress = preserve_progress
        self._frames_elapsed = 0
        self._transition_started = False

    def on_enter(self, game: "Game") -> None:
        self._frames_elapsed = 0
        self._transition_started = False
        game.world.reset(preserve_progress=self._preserve_progress)

    def update(self, game: "Game", dt: float) -> None:
        if self._transition_started or game.transitioning:
            return

        self._frames_elapsed += 1
        if self._frames_elapsed >= LIFE_SPLASH_FRAMES:
            self._begin_play(game)

    def draw_overlay(self, game: "Game", context: "RenderContext") -> None:
        surface = context.surface
        surface.fill(BLACK)

        hud = game.world.hud
        world_label = hud.level_label or "1-1"

        # Header: WORLD <label>
        world_text = f"WORLD {world_label}"
        header_y = (NATIVE_HEIGHT // 2) + SUB_TILE_SIZE * 4
        draw_centered_text(surface, world_text, header_y)

        # Mario avatar centered with life multiplier
        icon_y = (NATIVE_HEIGHT // 2) + SUB_TILE_SIZE
        icon_width = 2 * SUB_TILE_SIZE
        spacing = SUB_TILE_SIZE

        life_text = f"x {hud.lives}"
        life_text_width = len(life_text) * SUB_TILE_SIZE
        total_width = icon_width + spacing + life_text_width
        start_x = (NATIVE_WIDTH - total_width) // 2

        sprites.draw_at_position(surface, "objects", "mario_avatar", start_x, icon_y)
        text_x = start_x + icon_width + spacing
        draw_text(surface, life_text, text_x, icon_y)

    def _begin_play(self, game: "Game") -> None:
        if self._transition_started:
            return

        self._transition_started = True

        from ..rendering import TransitionMode
        from .start_level import StartLevelState

        game.transition(
            StartLevelState(preserve_progress=self._preserve_progress),
            TransitionMode.FADE_IN,
        )
