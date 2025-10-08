"""Effect manager for transient visual elements."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from pygame import Surface

from ..camera import Camera
from .base import Effect, EffectFactory


@dataclass(slots=True)
class EffectManager:
    """Maintains active transient effects."""

    _effects: List[Effect] = field(default_factory=list)

    def spawn(self, effect: Effect | EffectFactory) -> None:
        """Add a new effect or factory-produced effect to the manager."""
        if callable(effect):
            effect = effect()
        self._effects.append(effect)

    def extend(self, effects: Iterable[Effect]) -> None:
        """Add multiple effects at once."""
        self._effects.extend(effects)

    def update(self, dt: float) -> None:
        """Advance all active effects and cull finished ones."""
        active: List[Effect] = []
        for effect in self._effects:
            if effect.update(dt):
                active.append(effect)
        self._effects = active

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render all active effects."""
        for effect in self._effects:
            effect.draw(surface, camera)

    def clear(self) -> None:
        """Remove all active effects."""
        self._effects.clear()
