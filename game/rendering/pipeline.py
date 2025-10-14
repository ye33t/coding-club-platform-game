"""Layered renderer that draws ordered render layers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional

from game.constants import BACKGROUND_COLOR
from game.display import Display
from game.rendering.background import BackgroundLayer
from game.rendering.behind_drawables import BehindDrawablesLayer
from game.rendering.debug_overlay import DebugOverlayLayer
from game.rendering.front_drawables import FrontDrawablesLayer
from game.rendering.terrain import TerrainLayer

from .base import EffectLayer, RenderContext, RenderLayer

if TYPE_CHECKING:
    from ..game import Game


class RenderPipeline:
    """Renderer that processes ordered render layers each frame."""

    def __init__(self) -> None:
        self._display = Display()
        self._base_layers: List[RenderLayer] = [
            BackgroundLayer(),
            BehindDrawablesLayer(),
            TerrainLayer(),
            FrontDrawablesLayer(),
        ]
        self._debug_overlay = DebugOverlayLayer()
        self._overlays: List[RenderLayer] = []
        self._effect_layers: List[EffectLayer] = []

    def change_scale(self, scale: int) -> None:
        self._display.change_scale(scale)

    def toggle_debug(self) -> None:
        """Toggle the visibility of the debug overlay."""
        if self._debug_overlay in self._overlays:
            self._overlays.remove(self._debug_overlay)
        else:
            self._overlays.append(self._debug_overlay)

    def enqueue_effect(
        self,
        layer: EffectLayer,
    ) -> None:
        """Install or clear the post-process effect rendered last."""
        self._effect_layers.append(layer)

    def draw(self, game: Game) -> None:
        """Draw the game to the render pipeline"""
        while len(self._effect_layers) > 0:
            if self._effect_layers[0].complete():
                self._effect_layers.pop()
            else:
                self._effect_layers[0].update(game)
                break

        self._display.clear(BACKGROUND_COLOR)
        surface = self._display.get_native_surface()

        context = RenderContext(surface, game)
        for layer in self.layers:
            layer.draw(context)

        self._display.present()

    @property
    def layers(self) -> Iterable[RenderLayer]:
        """Get the list of all active render layers."""
        yield from self._base_layers
        yield from self._overlays
        if len(self._effect_layers) > 0:
            yield self._effect_layers[0]
