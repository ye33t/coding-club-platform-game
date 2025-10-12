"""Entity manager for active game entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, List

from pygame import Surface

from ..camera import Camera
from .base import Entity

if TYPE_CHECKING:
    from ..level import Level


@dataclass(slots=True)
class EntityManager:
    """Manages active game entities (enemies and collectibles)."""

    _entities: List[Entity] = field(default_factory=list)

    def spawn(self, entity: Entity) -> None:
        """Add a new entity to the manager.

        Args:
            entity: Entity to add
        """
        self._entities.append(entity)

    def remove(self, entity: Entity) -> None:
        """Remove an entity from the manager.

        Args:
            entity: Entity to remove
        """
        self._entities.remove(entity)

    def update(
        self, dt: float, level: Level, mario_screen: int, camera_x: float
    ) -> None:
        """Update all active entities and remove dead/off-screen ones.

        Args:
            dt: Delta time in seconds
            level: Level for collision detection
            mario_screen: Mario's current screen for culling
            camera_x: Camera X position for culling
        """
        active: List[Entity] = []
        for entity in self._entities:
            if entity.update(dt, level):
                if not entity.is_off_screen(mario_screen, camera_x):
                    active.append(entity)
        self._entities = active

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render all active entities.

        Args:
            surface: Surface to draw on
            camera: Camera for coordinate transformation
        """
        for entity in self._entities:
            entity.draw(surface, camera)

    def clear(self) -> None:
        """Remove all active entities."""
        self._entities.clear()

    @property
    def items(self) -> Iterable[Entity]:
        """Get an iterable of all active entities."""
        return iter(self._entities)
