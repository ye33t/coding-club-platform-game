"""Layered renderer that draws ordered render layers."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from pygame import Surface

from .base import RenderContext, RenderLayer

if TYPE_CHECKING:
    from ..game import Game


class RenderPipeline:
    """Renderer that processes ordered render layers each frame."""

    def __init__(self) -> None:
        self._layers: List[RenderLayer] = []

    def add_layer(self, layer: RenderLayer, game: "Game") -> None:
        """Append a new layer to the stack."""
        if layer in self._layers:
            return
        self._layers.append(layer)
        layer.on_added(game)

    def remove_layer(self, layer: RenderLayer, game: "Game") -> None:
        """Remove a layer from the stack."""
        if layer not in self._layers:
            return
        self._layers.remove(layer)
        layer.on_removed(game)

    def update(self, dt: float, game: "Game") -> None:
        """Update each layer and drop completed ones."""
        for layer in list(self._layers):
            if not layer.update(dt, game):
                self.remove_layer(layer, game)

    def draw(self, surface: Surface, game: "Game") -> None:
        """Draw each layer in order."""
        context = RenderContext(game)
        for layer in self._layers:
            layer.draw(surface, game, context)
