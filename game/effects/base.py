"""Common interfaces for transient visual effects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from pygame import Surface

from ..camera import Camera


class Effect(ABC):
    """Simple lifecycle for transient effects."""

    @abstractmethod
    def update(self, dt: float) -> bool:
        """Advance effect state.

        Args:
            dt: Delta time in seconds since last update.

        Returns:
            True if the effect remains active, False when it should be removed.
        """

    @abstractmethod
    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the effect to the given surface."""


class EffectFactory(Protocol):
    """Callable signature for deferred effect construction."""

    @abstractmethod
    def __call__(self) -> Effect:
        """Produce a new effect instance."""
