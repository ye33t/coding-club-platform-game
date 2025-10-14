"""Base types for layered rendering."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Iterator, Protocol

if TYPE_CHECKING:
    from pygame import Surface

    from ..camera import Camera
    from ..game import Game
    from ..level import Level
    from ..mario import Mario
    from ..world import World


class Drawable(Protocol):
    """Renderable object that can sort itself via z-index."""

    z_index: int

    def draw(self, surface: "Surface", camera: "Camera") -> None:
        """Render the drawable to the surface using the provided camera."""


class RenderContext:
    """Shared rendering data computed once per frame."""

    def __init__(self, surface: Surface, game: Game) -> None:
        self._surface = surface
        self._game = game

    @property
    def surface(self) -> Surface:
        return self._surface

    @property
    def game(self) -> "Game":
        return self._game

    @property
    def drawables(self) -> Iterator[Drawable]:
        return self._game.world.drawables

    @property
    def world(self) -> World:
        return self._game.world

    @property
    def level(self) -> Level:
        return self._game.world.level

    @property
    def mario(self) -> Mario:
        return self._game.world.mario

    @property
    def camera(self) -> Camera:
        return self._game.world.camera

    @property
    def behind_drawables(self) -> Iterator[Drawable]:
        return self._layered_drawables(lambda drawable: drawable.z_index < 0)

    @property
    def front_drawables(self) -> Iterator[Drawable]:
        return self._layered_drawables(lambda drawable: drawable.z_index >= 0)

    def _layered_drawables(
        self,
        predicate: Callable[[Drawable], bool],
    ) -> Iterator[Drawable]:
        def _iter() -> Iterator[Drawable]:
            filtered = (
                drawable
                for drawable in self._game.world.drawables
                if predicate(drawable)
            )
            for drawable in sorted(
                filtered,
                key=lambda candidate: candidate.z_index,
            ):
                yield drawable

        return _iter()


class RenderLayer(ABC):
    """Single layer in the renderer stack."""

    def on_added(self, game: "Game") -> None:
        """Hook invoked when the layer is added to the renderer."""

    def update(self, dt: float, game: "Game") -> bool:
        """Advance layer state. Return False to remove the layer."""
        return True

    @abstractmethod
    def draw(
        self,
        context: RenderContext,
    ) -> None:
        """Render the layer."""
