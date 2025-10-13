"""Base types for layered rendering."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from pygame import Surface

    from ..game import Game


class RenderContext:
    """Shared rendering data computed once per frame."""

    def __init__(self, game: "Game") -> None:
        self._game = game
        self._drawables: Optional[List[Any]] = None
        self._behind: Optional[List[Any]] = None
        self._front: Optional[List[Any]] = None

    @property
    def game(self) -> "Game":
        return self._game

    @property
    def drawables(self) -> List[Any]:
        if self._drawables is None:
            self._drawables = list(self._game.world.drawables)
        return self._drawables

    @property
    def behind_drawables(self) -> List[Any]:
        if self._behind is None:
            self._prepare_drawable_layers()
        return self._behind or []

    @property
    def front_drawables(self) -> List[Any]:
        if self._front is None:
            self._prepare_drawable_layers()
        return self._front or []

    def _prepare_drawable_layers(self) -> None:
        behind: List[Any] = []
        front: List[Any] = []

        for drawable in self.drawables:
            target = behind if getattr(drawable, "z_index", 0) < 0 else front
            target.append(drawable)

        behind.sort(key=lambda d: getattr(d, "z_index", 0))
        front.sort(key=lambda d: getattr(d, "z_index", 0))

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
