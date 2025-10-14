"""Layered renderer that draws ordered render layers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence

from pygame import Surface

from .base import RenderContext, RenderLayer

if TYPE_CHECKING:
    from ..game import Game


class RenderPipeline:
    """Renderer that processes ordered render layers each frame."""

    def __init__(self) -> None:
        self._base_layers: List[RenderLayer] = []
        self._overlays: List[RenderLayer] = []
        self._effect_layer: Optional[RenderLayer] = None

    def configure_base_layers(
        self,
        layers: Sequence[RenderLayer],
        game: "Game",
    ) -> None:
        """Install the static rendering passes executed every frame."""
        self._base_layers = list(layers)
        self._attach_layers(self._base_layers, game)

    def overlays(self) -> Iterable[RenderLayer]:
        return tuple(self._overlays)

    def effect(self) -> Optional[RenderLayer]:
        return self._effect_layer

    def add_overlay(self, layer: RenderLayer, game: "Game") -> None:
        """Add a transient overlay that renders after base layers."""
        if layer in self._overlays:
            return
        self._overlays.append(layer)
        layer.on_added(game)

    def remove_overlay(self, layer: RenderLayer, game: "Game") -> None:
        """Remove a previously attached overlay."""
        if layer not in self._overlays:
            return
        self._overlays.remove(layer)

    def set_effect(
        self,
        layer: Optional[RenderLayer],
        game: "Game",
    ) -> None:
        """Install or clear the post-process effect rendered last."""
        if layer is self._effect_layer:
            return
        self._effect_layer = layer
        if self._effect_layer is not None:
            self._effect_layer.on_added(game)

    def update(self, dt: float, game: "Game") -> None:
        """Update each layer and drop completed ones."""
        self._update_layers(self._base_layers, dt, game)
        self._update_layers(self._overlays, dt, game)

        if self._effect_layer is not None:
            if not self._effect_layer.update(dt, game):
                self.set_effect(None, game)

    def draw(self, surface: Surface, game: "Game") -> None:
        """Draw each layer in order."""
        context = RenderContext(surface, game)
        for layer in self._base_layers:
            layer.draw(context)
        for layer in self._overlays:
            layer.draw(context)
        if self._effect_layer is not None:
            self._effect_layer.draw(context)

    def _update_layers(
        self,
        layers: List[RenderLayer],
        dt: float,
        game: "Game",
    ) -> None:
        for layer in list(layers):
            if not layer.update(dt, game):
                layers.remove(layer)

    def _attach_layers(
        self,
        layers: Iterable[RenderLayer],
        game: "Game",
    ) -> None:
        for layer in layers:
            layer.on_added(game)
