"""Overlay layers such as transitions and debug visualization."""

from __future__ import annotations

import math
from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

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


class TransitionLayer(EffectLayer):
    """Circular iris transition overlay."""

    def __init__(
        self,
        mode: TransitionMode,
        on_transition: Callable[[], None]
    ) -> None:
        self._mode = mode
        self._on_transition = on_transition
        self._elapsed = 0.0
        self._triggered = False
        self._complete = False
        
    def complete(self) -> bool:
        return self._complete

    def update(self, game: Game) -> None:
        self._elapsed += game.dt
        
        if self._elapsed >= self.trigger_time and not self._triggered:
            print(f"Triggered at {self._elapsed:.2f}s {self._mode}")
            self._on_transition()
            self._triggered = True

        if self._elapsed >= self.duration:
            print(f"Complete at {self._elapsed:.2f}s {self._mode}")
            self._complete = True

    def draw(
        self,
        context: RenderContext,
    ) -> None:
        if self._complete:
            return
        
        progress = (
            1.0 if self.duration <= 0 else min(1.0, self._elapsed / self.duration)
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
        context.surface.blit(mask, (0, 0))

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
