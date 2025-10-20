"""Entity manager for active game entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, List, Optional, Set

from pygame import Surface

from ..camera import Camera
from .base import Entity

if TYPE_CHECKING:
    from ..level import Level


@dataclass(slots=True)
class EntityManager:
    """Manages active game entities (enemies and collectibles)."""

    _entities: List[Entity] = field(default_factory=list)
    _enemy_defeat_handler: Optional[
        Callable[[Entity, Entity, tuple[float, float]], None]
    ] = None

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
        self._handle_entity_collisions()

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

    def set_enemy_defeat_handler(
        self,
        handler: Optional[Callable[[Entity, Entity, tuple[float, float]], None]],
    ) -> None:
        """Install a callback invoked when an entity is defeated by another."""

        self._enemy_defeat_handler = handler

    def _handle_entity_collisions(self) -> None:
        to_remove: Set[Entity] = set()

        sources = [
            entity
            for entity in self._entities
            if entity.can_damage_entities or entity.blocks_entities
        ]

        if not sources:
            return

        for source in sources:
            source_rect = source.get_collision_bounds()

            for target in self._entities:
                if target is source or target in to_remove:
                    continue

                if not source_rect.colliderect(target.get_collision_bounds()):
                    continue

                if source.can_damage_entities and target.can_be_damaged_by_entities:
                    defeated_before = self._is_defeated(target)
                    if target.on_collide_entity(source):
                        to_remove.add(target)
                    defeated_after = self._is_defeated(target)
                    if (
                        self._enemy_defeat_handler is not None
                        and not defeated_before
                        and defeated_after
                        and target.awards_shell_combo
                    ):
                        impact_position = (
                            target.state.x + target.state.width / 2,
                            target.state.y + target.state.height,
                        )
                        self._enemy_defeat_handler(source, target, impact_position)
                    continue

                if source.blocks_entities:
                    target.on_collide_entity(source)

        if to_remove:
            self._entities = [
                entity for entity in self._entities if entity not in to_remove
            ]

    @staticmethod
    def _is_defeated(entity: Entity) -> bool:
        return bool(
            getattr(entity, "knocked_out", False) or getattr(entity, "is_dead", False)
        )
