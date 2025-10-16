"""Manager for world props."""

from __future__ import annotations

from typing import Dict, Iterator

from .base import Prop


class PropManager:
    """Tracks and updates decorative props."""

    def __init__(self) -> None:
        self._props: Dict[str, Prop] = {}

    def register(self, key: str, prop: Prop) -> None:
        """Register a prop so it participates in spawn/reset/update."""
        self._props[key] = prop

    def spawn_all(self, world) -> None:
        """Spawn all registered props."""
        for prop in self._props.values():
            prop.spawn(world)

    def reset(self, world) -> None:
        """Reset all registered props to their initial state."""
        for prop in self._props.values():
            prop.reset(world)

    def update(self, world, dt: float) -> None:
        """Advance all props."""
        for prop in self._props.values():
            prop.update(world, dt)

    def get(self, key: str) -> Prop | None:
        """Retrieve a prop by key."""
        return self._props.get(key)

    def items(self) -> Iterator[tuple[str, Prop]]:
        """Iterate over registered props with their keys."""
        return iter(self._props.items())
