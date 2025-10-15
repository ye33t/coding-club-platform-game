"""Entity factory for creating game entities from spawn specifications."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import Entity
from .goomba import GoombaEntity
from .koopa import KoopaTroopaEntity, ShellEntity
from .mushroom import MushroomEntity


class EntityFactory:
    """Factory for creating entities from spawn specifications."""

    def create(
        self,
        entity_type: str,
        world_x: float,
        world_y: float,
        screen: int = 0,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Entity]:
        """Create an entity from a spawn specification.

        Args:
            entity_type: Type of entity to create (e.g., "goomba", "mushroom")
            world_x: X position in world pixels
            world_y: Y position in screen-relative pixels (0-224, from bottom)
            screen: Which vertical screen the entity is on
            params: Optional parameters for entity creation

        Returns:
            Created entity, or None if type is unknown
        """
        params = params or {}

        if entity_type == "goomba":
            facing_right = self._parse_facing(params.get("facing", "left"))
            return GoombaEntity(world_x, world_y, screen, facing_right)

        elif entity_type == "mushroom":
            facing_right = self._parse_facing(params.get("facing", "right"))
            return MushroomEntity(world_x, world_y, screen, facing_right)

        elif entity_type == "koopa_troopa":
            facing_right = self._parse_facing(params.get("facing", "left"))
            return KoopaTroopaEntity(world_x, world_y, screen, facing_right)

        elif entity_type == "koopa_shell":
            facing_right = self._parse_facing(params.get("facing", "left"))
            return ShellEntity(world_x, world_y, screen, facing_right)

        # Unknown entity type
        return None

    def _parse_facing(self, facing: str) -> bool:
        """Parse facing direction into a boolean flag."""
        normalized = facing.strip().lower()
        return normalized == "right"
