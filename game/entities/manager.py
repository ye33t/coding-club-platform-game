"""Entity manager for active game entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

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

    def get_entities(self) -> List[Entity]:
        """Get list of active entities.

        Returns:
            List of all active entities
        """
        return self._entities.copy()

    def clear(self) -> None:
        """Remove all active entities."""
        self._entities.clear()
