"""Transition effect and supporting timeline helpers."""

from __future__ import annotations

import math
from enum import Enum
from typing import TYPE_CHECKING

import pygame

from ..constants import BACKGROUND_COLOR, BLACK, NATIVE_HEIGHT, NATIVE_WIDTH
from .base import EffectLayer, RenderContext

if TYPE_CHECKING:
    from ..game import Game


class TransitionMode(Enum):
    """Transition animation mode for scene changes."""

    INSTANT = "instant"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    BOTH = "both"


class TransitionTimeline:
    """Tiny state machine that tracks transition progress and swap timing."""

    def __init__(self, mode: TransitionMode) -> None:
        self._mode = mode
        self._elapsed = 0.0
        self._state_swapped = False

    @property
    def mode(self) -> TransitionMode:
        return self._mode

    @property
    def duration(self) -> float:
        return {
            TransitionMode.INSTANT: 0.0,
            TransitionMode.FADE_IN: 1.0,
            TransitionMode.FADE_OUT: 1.0,
            TransitionMode.BOTH: 2.0,
        }[self._mode]

    @property
    def trigger_time(self) -> float:
        return {
            TransitionMode.INSTANT: 0.0,
            TransitionMode.FADE_IN: 0.0,
            TransitionMode.FADE_OUT: self.duration,
            TransitionMode.BOTH: self.duration / 2,
        }[self._mode]

    @property
    def progress(self) -> float:
        if self.duration <= 0:
            return 1.0
        return min(1.0, self._elapsed / self.duration)

    @property
    def is_complete(self) -> bool:
        return self._elapsed >= self.duration

    def advance(self, dt: float) -> None:
        if self.is_complete:
            return
        self._elapsed = min(self.duration, self._elapsed + max(0.0, dt))

    def ready_for_state_swap(self) -> bool:
        return not self._state_swapped and self._elapsed >= self.trigger_time

    def mark_state_swapped(self) -> None:
        self._state_swapped = True


class TransitionLayer(EffectLayer):
    """Circular iris transition overlay driven by a shared timeline."""

    def __init__(self, timeline: TransitionTimeline) -> None:
        self._timeline = timeline

    def complete(self) -> bool:
        return self._timeline.is_complete

    def update(self, game: "Game") -> None:
        self._timeline.advance(game.dt)

    def draw(
        self,
        context: RenderContext,
    ) -> None:
        if self._timeline.is_complete:
            return

        progress = self._timeline.progress
        max_radius = math.hypot(NATIVE_WIDTH / 2, NATIVE_HEIGHT / 2)

        if self._timeline.mode == TransitionMode.FADE_OUT:
            eased = progress * progress * (3 - 2 * progress)
            radius = max_radius * (1 - eased)
        elif self._timeline.mode == TransitionMode.FADE_IN:
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
        context.surface.blit(mask, (0, 0))
