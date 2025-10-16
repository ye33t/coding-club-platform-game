"""Base classes for the reusable entity physics pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ...level import Level
    from ..base import Entity, EntityState


@dataclass(slots=True)
class EntityPhysicsContext:
    """Context object that flows through entity physics processors."""

    entity: "Entity"
    state: "EntityState"
    level: "Level"
    dt: float


class EntityProcessor(Protocol):
    """Protocol for entity physics processors."""

    def process(self, context: EntityPhysicsContext) -> EntityPhysicsContext:
        """Process the entity physics context and return it."""
        ...
