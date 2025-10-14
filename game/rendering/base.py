"""Base types for layered rendering."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional, Protocol

if TYPE_CHECKING:
    from pygame import Surface

    from ..camera import Camera
    from ..game import Game


class Drawable(Protocol):
    """Renderable object that can sort itself via z-index."""

    z_index: int

    def draw(self, surface: "Surface", camera: "Camera") -> None:
        """Render the drawable to the surface using the provided camera."""


class RenderContext:
    """Shared rendering data computed once per frame."""

    def __init__(self, game: "Game") -> None:
        self._game = game
        self._drawables: Optional[List[Drawable]] = None
        self._behind: Optional[List[Drawable]] = None
        self._front: Optional[List[Drawable]] = None

    @property
    def game(self) -> "Game":
        return self._game

    @property
    def drawables(self) -> List[Drawable]:
        if self._drawables is None:
            self._drawables = list(self._game.world.drawables)
        return self._drawables

    @property
    def behind_drawables(self) -> List[Drawable]:
        if self._behind is None:
            self._prepare_drawable_layers()
        return self._behind or []

    @property
    def front_drawables(self) -> List[Drawable]:
        if self._front is None:
            self._prepare_drawable_layers()
        return self._front or []

    def _prepare_drawable_layers(self) -> None:
        behind: List[Drawable] = []
        front: List[Drawable] = []

        for drawable in self.drawables:
            target = behind if drawable.z_index < 0 else front
            target.append(drawable)

        behind.sort(key=lambda d: d.z_index)
        front.sort(key=lambda d: d.z_index)

        self._behind = behind
        self._front = front


class RenderLayer(ABC):
    """Single layer in the renderer stack."""

    def on_added(self, game: "Game") -> None:
        """Hook invoked when the layer is added to the renderer."""

    def on_removed(self, game: "Game") -> None:
        """Hook invoked when the layer is removed from the renderer."""

    def update(self, dt: float, game: "Game") -> bool:
        """Advance layer state. Return False to remove the layer."""
        return True

    @abstractmethod
    def draw(
        self,
        surface: "Surface",
        game: "Game",
        context: RenderContext,
    ) -> None:
        """Render the layer."""
