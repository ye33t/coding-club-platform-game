"""Render layer for drawables positioned at or above terrain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import RenderContext, RenderLayer

if TYPE_CHECKING:
    from pygame import Surface

    from ..game import Game
    from ..world import World


class ForegroundDrawablesLayer(RenderLayer):
    """Draws drawables positioned at or above terrain."""

    def __init__(self, world: "World") -> None:
        self._world = world

    def draw(
        self,
        surface: "Surface",
        game: "Game",
        context: RenderContext,
    ) -> None:
        for drawable in context.front_drawables:
            drawable.draw(surface, self._world.camera)
