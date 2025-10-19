"""Layered renderer that draws ordered render layers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional

from game.content import palettes
from game.display import Display
from game.rendering.background import BackgroundLayer
from game.rendering.behind_background_drawables import BehindBackgroundDrawablesLayer
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
            BehindBackgroundDrawablesLayer(),
            BackgroundLayer(),
            BehindDrawablesLayer(),
            TerrainLayer(),
            FrontDrawablesLayer(),
        ]
        self._debug_overlay = DebugOverlayLayer()
        self._overlays: List[RenderLayer] = []
        self._effect_layer: Optional[EffectLayer] = None

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
        if layer.complete():
            return

        if self._effect_layer is None:
            self._effect_layer = layer
        else:
            raise RuntimeError("Cannot enqueue effect while another is active")

    def draw(self, game: Game) -> None:
        """Draw the game to the render pipeline"""
        if self._effect_layer is not None:
            if self._effect_layer.complete():
                self._effect_layer = None
            else:
                self._effect_layer.update(game)

        level = game.world.level
        screen_palette = level.get_palette_for_screen(game.world.mario.screen)
        try:
            palettes.get_scheme(screen_palette)
            palette_choice = screen_palette
        except KeyError:
            palette_choice = None

        with palettes.activate(palette_choice) as scheme:
            self._display.clear(scheme.background)
            surface = self._display.get_native_surface()

            context = RenderContext(surface, game, scheme)
            for layer in self.layers:
                layer.draw(context)

            self._display.present()

    @property
    def layers(self) -> Iterable[RenderLayer]:
        """Get the list of all active render layers."""
        yield from self._base_layers
        yield from self._overlays
        if self._effect_layer is not None:
            yield self._effect_layer
