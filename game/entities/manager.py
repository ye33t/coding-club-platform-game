"""Entity manager for active game entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Set

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
        self._handle_shell_collisions()

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
    def items(self) -> List[Entity]:
        """Get an iterable of all active entities."""
        return self._entities

    def _handle_shell_collisions(self) -> None:
        """Resolve moving shell collisions with other entities."""
        damage_sources = [
            entity for entity in self._entities if entity.can_damage_entities
        ]

        if not damage_sources:
            return

        to_remove: Set[Entity] = set()

        for source in damage_sources:
            source_rect = source.get_collision_bounds()

            for entity in self._entities:
                if entity is source or entity in to_remove:
                    continue

                if not entity.can_be_damaged_by_entities:
                    continue

                if not source_rect.colliderect(entity.get_collision_bounds()):
                    continue

                if entity.on_collide_entity(source):
                    to_remove.add(entity)

        if to_remove:
            self._entities = [
                entity for entity in self._entities if entity not in to_remove
            ]
