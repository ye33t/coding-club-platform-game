"""Final castle sequence state after the flagpole."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pygame

from game.constants import SUB_TILE_SIZE
from game.mario import MarioIntent

from ..effects import SpriteEffect
from ..physics.config import FLAGPOLE_DESCENT_SPEED
from ..rendering import TransitionMode
from .base import State

FLAG_X_OFFSET = SUB_TILE_SIZE - 2
CASTLE_FLAG_SPEED_SCALE = 0.6
CASTLE_COMPLETION_DELAY = 1.0


@dataclass(frozen=True)
class CastleWalkAnchor:
    """World-space anchor describing the castle entrance."""

    screen: int
    world_x: float
    world_y: float


@dataclass(frozen=True)
class CastleFlagAnchor:
    """World-space anchor for the castle flag raising animation."""

    screen: int
    world_x: float
    final_y: float
    initial_y: float


class CompleteLevelState(State):
    """State that hides Mario and raises the castle flag."""

    def __init__(
        self,
        walk_anchor: CastleWalkAnchor | None,
        flag_anchor: CastleFlagAnchor | None,
    ) -> None:
        self._walk_anchor = walk_anchor
        self._flag_anchor = flag_anchor

        self._flag_effect: Optional[SpriteEffect] = None
        self._current_flag_y: Optional[float] = None
        self._flag_finished: bool = flag_anchor is None

        self._flag_raise_speed = FLAGPOLE_DESCENT_SPEED * CASTLE_FLAG_SPEED_SCALE
        self._completion_timer = 0.0

    def on_enter(self, game) -> None:
        """Prepare the castle finale sequence."""
        self._prepare_mario(game.world.mario)

        if self._flag_anchor is not None:
            self._spawn_flag_effect(game)
        else:
            self._flag_finished = True

    def update(self, game, dt: float) -> None:
        """Advance the flag animation and finish the level."""
        self._update_flag_raise(dt)

        if self._flag_finished:
            self._tick_completion_timer(game, dt)

        game.world.effects.update(dt)

    def on_exit(self, game) -> None:
        """Clean up spawned effects and restore Mario visibility."""
        mario = game.world.mario
        mario.visible = True
        mario.set_intent_override(None)

        self._deactivate_flag_effect()

    def _prepare_mario(self, mario) -> None:
        """Hide Mario and clear player input."""

        def _empty_intent(_: pygame.key.ScancodeWrapper) -> MarioIntent:
            return MarioIntent()

        mario.set_intent_override(_empty_intent)

        mario.vx = 0.0
        mario.vy = 0.0
        mario.visible = False

    def _spawn_flag_effect(self, game) -> None:
        """Spawn the castle flag animation effect."""
        if self._flag_anchor is None:
            return

        self._flag_effect = SpriteEffect(
            sprite_sheet="objects",
            sprite_name="flag_castle",
            world_x=self._flag_anchor.world_x,
            world_y=self._flag_anchor.initial_y,
            z_index=-20,
        )
        self._current_flag_y = self._flag_anchor.initial_y
        game.world.effects.spawn(self._flag_effect)

    def _update_flag_raise(self, dt: float) -> None:
        """Move the castle flag toward its final resting position."""
        if (
            self._flag_finished
            or self._flag_anchor is None
            or self._flag_effect is None
            or self._current_flag_y is None
        ):
            self._flag_finished = True
            return

        next_y = self._current_flag_y + self._flag_raise_speed * dt
        if next_y >= self._flag_anchor.final_y:
            next_y = self._flag_anchor.final_y
            self._flag_finished = True

        self._current_flag_y = next_y
        self._flag_effect.set_position(
            self._flag_anchor.world_x + FLAG_X_OFFSET,
            next_y,
        )

    def _tick_completion_timer(self, game, dt: float) -> None:
        """Wait briefly before returning control to the start state."""
        if game.transitioning:
            return

        self._completion_timer += dt
        if self._completion_timer < CASTLE_COMPLETION_DELAY:
            return

        from .life_splash import LifeSplashState

        game.transition(
            LifeSplashState(preserve_progress=True), TransitionMode.FADE_OUT
        )

    def _deactivate_flag_effect(self) -> None:
        """Ensure the spawned flag effect is cleaned up."""
        if self._flag_effect is None:
            return
        self._flag_effect.deactivate()
        self._flag_effect = None
