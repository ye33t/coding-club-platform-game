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

        self._flag_raise_speed = FLAGPOLE_DESCENT_SPEED * 0.6
        self._completion_delay = 1.0
        self._completion_timer = 0.0

    def on_enter(self, game) -> None:
        """Prepare the castle finale sequence."""
        mario = game.world.mario

        def _empty_intent(_: pygame.key.ScancodeWrapper) -> MarioIntent:
            return MarioIntent()

        mario.set_intent_override(_empty_intent)

        mario.vx = 0.0
        mario.vy = 0.0
        mario.visible = False

        if self._flag_anchor is not None:
            self._flag_effect = SpriteEffect(
                sprite_sheet="other",
                sprite_name="flag_castle",
                world_x=self._flag_anchor.world_x,
                world_y=self._flag_anchor.initial_y,
                z_index=-20,
            )
            self._current_flag_y = self._flag_anchor.initial_y
            game.world.effects.spawn(self._flag_effect)
        else:
            self._flag_finished = True

    def update(self, game, dt: float) -> None:
        """Advance the flag animation and finish the level."""
        if (
            not self._flag_finished
            and self._flag_anchor
            and self._flag_effect
            and self._current_flag_y is not None
        ):
            next_y = self._current_flag_y + self._flag_raise_speed * dt
            if next_y >= self._flag_anchor.final_y:
                next_y = self._flag_anchor.final_y
                self._flag_finished = True
            self._current_flag_y = next_y
            self._flag_effect.set_position(
                self._flag_anchor.world_x + FLAG_X_OFFSET, next_y
            )
        else:
            self._completion_timer += dt
            if (
                self._completion_timer >= self._completion_delay
                and not game.transitioning
            ):
                from .start_level import StartLevelState

                game.transition(StartLevelState(), TransitionMode.BOTH)

        game.world.effects.update(dt)

    def on_exit(self, game) -> None:
        """Clean up spawned effects and restore Mario visibility."""
        mario = game.world.mario
        mario.visible = True
        mario.set_intent_override(None)

        if self._flag_effect is not None:
            self._flag_effect.deactivate()
            self._flag_effect = None
