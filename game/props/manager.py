"""Manager for world props."""

from __future__ import annotations

from typing import List

from .base import Prop


class PropManager:
    """Tracks and updates decorative props."""

    def __init__(self) -> None:
        self._props: List[Prop] = []

    def register(self, prop: Prop) -> None:
        """Register a prop so it participates in spawn/reset/update."""
        self._props.append(prop)

    def spawn_all(self, world) -> None:
        """Spawn all registered props."""
        for prop in self._props:
            prop.spawn(world)

    def reset(self, world) -> None:
        """Reset all registered props to their initial state."""
        for prop in self._props:
            prop.reset(world)

    def update(self, world, dt: float) -> None:
        """Advance all props."""
        for prop in self._props:
            prop.update(world, dt)
