"""Final castle sequence state after the flagpole."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pygame

from game.constants import SUB_TILE_SIZE, TILE_SIZE
from game.mario import MarioIntent

from ..effects import FireworkEffect, SpriteEffect
from ..physics.config import FLAGPOLE_DESCENT_SPEED
from ..rendering import TransitionMode
from .base import State

FLAG_X_OFFSET = SUB_TILE_SIZE - 2
CASTLE_FLAG_SPEED_SCALE = 0.6
CASTLE_COMPLETION_DELAY = 1.0
FIREWORK_SCORE_VALUE = 500
FIREWORK_SPAWN_INTERVAL = 0.45
FIREWORK_VERTICAL_SHIFT_TILES = 5.0
FIREWORK_OFFSET_TILES: tuple[tuple[float, float], ...] = (
    (-2.5, 3.5),
    (2.5, 3.0),
    (0.0, 4.5),
    (-3.5, 2.5),
    (3.5, 4.0),
    (1.0, 5.0),
)


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


@dataclass(slots=True)
class FireworkPlan:
    """Scheduled firework burst relative to the castle."""

    spawn_time: float
    world_x: float
    world_y: float


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
        self._firework_queue: list[FireworkPlan] = []
        self._firework_clock = 0.0
        self._active_fireworks = 0
        self._fireworks_enabled = False

    def on_enter(self, game) -> None:
        """Prepare the castle finale sequence."""
        self._prepare_mario(game.world.mario)
        self._fireworks_enabled = True
        self._completion_timer = 0.0
        self._schedule_fireworks(game)

        if self._flag_anchor is not None:
            self._spawn_flag_effect(game)
        else:
            self._flag_finished = True

    def update(self, game, dt: float) -> None:
        """Advance the flag animation and finish the level."""
        self._update_flag_raise(dt)
        self._update_fireworks(game, dt)

        if self._flag_finished and self._fireworks_done():
            self._tick_completion_timer(game, dt)

        game.world.effects.update(dt)

    def on_exit(self, game) -> None:
        """Clean up spawned effects and restore Mario visibility."""
        mario = game.world.mario
        mario.visible = True
        mario.set_intent_override(None)

        self._deactivate_flag_effect()
        self._firework_queue.clear()
        self._firework_clock = 0.0
        self._active_fireworks = 0
        self._fireworks_enabled = False

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

    def _schedule_fireworks(self, game) -> None:
        """Prepare timed firework bursts based on the remaining timer digit."""
        self._firework_queue.clear()
        self._firework_clock = 0.0
        self._active_fireworks = 0

        count = self._determine_firework_count(game.world.hud.timer_value)
        if count <= 0 or self._walk_anchor is None:
            return

        anchor_x, anchor_y = self._firework_anchor_position()
        for index in range(count):
            offset_x, offset_y = FIREWORK_OFFSET_TILES[
                index % len(FIREWORK_OFFSET_TILES)
            ]
            world_x = anchor_x + offset_x * TILE_SIZE
            world_y = anchor_y + (offset_y - FIREWORK_VERTICAL_SHIFT_TILES) * TILE_SIZE
            spawn_time = index * FIREWORK_SPAWN_INTERVAL
            self._firework_queue.append(
                FireworkPlan(spawn_time=spawn_time, world_x=world_x, world_y=world_y)
            )

    @staticmethod
    def _determine_firework_count(timer_value: int) -> int:
        """Return the number of fireworks derived from the timer's last digit."""
        lookup = {1: 1, 3: 3, 6: 6}
        return lookup.get(timer_value % 10, 0)

    def _firework_anchor_position(self) -> tuple[float, float]:
        """Anchor fireworks around the castle flag or entry."""
        if self._flag_anchor is not None:
            base_x = self._flag_anchor.world_x
            base_y = self._flag_anchor.final_y + 2 * TILE_SIZE
        elif self._walk_anchor is not None:
            base_x = self._walk_anchor.world_x
            base_y = self._walk_anchor.world_y + 2 * TILE_SIZE
        else:
            base_x = 0.0
            base_y = 0.0
        return base_x, base_y

    def _update_fireworks(self, game, dt: float) -> None:
        """Spawn scheduled fireworks and let the effect manager animate them."""
        if not self._fireworks_enabled:
            return

        self._firework_clock += dt
        while (
            self._firework_queue
            and self._firework_clock >= self._firework_queue[0].spawn_time
        ):
            plan = self._firework_queue.pop(0)
            self._spawn_firework(game, plan)

    def _spawn_firework(self, game, plan: FireworkPlan) -> None:
        """Instantiate a firework effect at the configured position."""
        self._active_fireworks += 1

        def _finished_callback() -> None:
            self._handle_firework_finished(game, plan.world_x, plan.world_y)

        effect = FireworkEffect(
            world_x=plan.world_x,
            world_y=plan.world_y,
            z_index=-15,
            on_finished=_finished_callback,
        )
        game.world.effects.spawn(effect)

    def _handle_firework_finished(self, game, world_x: float, world_y: float) -> None:
        """Award score once a firework completes its animation."""
        if not self._fireworks_enabled:
            return

        self._active_fireworks = max(0, self._active_fireworks - 1)
        game.world.award_score_with_popup(FIREWORK_SCORE_VALUE, (world_x, world_y))

    def _fireworks_done(self) -> bool:
        """Whether all scheduled fireworks have spawned and finished."""
        return not self._firework_queue and self._active_fireworks == 0

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
