"""Composable renderer pipeline with post-processing effects."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from .base import RenderEffect, Renderer

if TYPE_CHECKING:
    from pygame import Surface

    from ..game import Game


class PipelineRenderer(Renderer):
    """Renderer that delegates to a base renderer and applies effects."""

    def __init__(self, base: Renderer):
        self._base = base
        self._effects: List[RenderEffect] = []

    @property
    def effects(self) -> List[RenderEffect]:
        """Get the mutable list of effects."""
        return self._effects

    def add_effect(self, effect: RenderEffect, game: "Game") -> None:
        """Add a new effect to the pipeline."""
        self._effects.append(effect)
        effect.on_add(game)

    def remove_effect(self, effect: RenderEffect, game: "Game") -> None:
        """Remove an existing effect."""
        if effect in self._effects:
            self._effects.remove(effect)
            effect.on_remove(game)

    def clear_effects(self, game: "Game") -> None:
        """Remove all effects from the pipeline."""
        for effect in self._effects:
            effect.on_remove(game)
        self._effects.clear()

    def update(self, dt: float, game: "Game") -> None:
        """Update active effects."""
        for effect in list(self._effects):
            if not effect.update(dt, game):
                self.remove_effect(effect, game)

    def draw(self, surface: "Surface", game: "Game") -> None:
        """Draw base renderer and apply active effects."""
        self._base.draw(surface, game)
        for effect in self._effects:
            effect.apply(surface, game)
