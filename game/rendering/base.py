"""Base types for rendering pipeline."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface

    from ..game import Game


class Renderer(ABC):
    """Abstract base renderer for producing a frame."""

    @abstractmethod
    def draw(self, surface: "Surface", game: "Game") -> None:
        """Draw the renderer's contents onto the provided surface."""


class RenderEffect(ABC):
    """Post-processing effect applied after the base renderer."""

    def on_add(self, game: "Game") -> None:
        """Hook called when the effect is added to the pipeline."""

    def on_remove(self, game: "Game") -> None:
        """Hook called when the effect is removed from the pipeline."""

    def update(self, dt: float, game: "Game") -> bool:
        """Advance effect state.

        Returns:
            True if the effect remains active, False when it should be removed.
        """
        return True

    @abstractmethod
    def apply(self, surface: "Surface", game: "Game") -> None:
        """Render the effect on top of the surface."""
