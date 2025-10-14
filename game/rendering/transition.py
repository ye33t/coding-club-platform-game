"""Overlay layers such as transitions and debug visualization."""

from __future__ import annotations

import math
from enum import Enum
from typing import TYPE_CHECKING, Callable, Optional

import pygame

from ..constants import BACKGROUND_COLOR, BLACK, NATIVE_HEIGHT, NATIVE_WIDTH
from .base import RenderContext, RenderLayer

if TYPE_CHECKING:
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
        context.surface.blit(mask, (0, 0))
