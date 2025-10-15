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
            direction = self._parse_direction(params.get("facing", "left"))
            return GoombaEntity(world_x, world_y, screen, direction)

        elif entity_type == "mushroom":
            direction = self._parse_direction(params.get("facing", "right"))
            return MushroomEntity(world_x, world_y, screen, direction)

        elif entity_type == "koopa_troopa":
            direction = self._parse_direction(params.get("facing", "left"))
            return KoopaTroopaEntity(world_x, world_y, screen, direction)

        elif entity_type == "koopa_shell":
            direction = self._parse_direction(params.get("facing", "left"))
            return ShellEntity(world_x, world_y, screen, direction)

        # Unknown entity type
        return None

    def _parse_direction(self, facing: str) -> int:
        """Parse a facing direction string into a direction value.

        Args:
            facing: Direction string ("left" or "right")

        Returns:
            -1 for left, 1 for right
        """
        if facing == "left":
            return -1
        elif facing == "right":
            return 1
        else:
            # Default to left if unknown
            return -1
