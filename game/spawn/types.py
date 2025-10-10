"""Spawn system data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass(slots=True)
class SpawnSpec:
    """Specification for spawning an entity."""

    entity_type: str  # e.g., "goomba", "mushroom"
    params: Dict[str, Any]  # Entity-specific parameters like facing direction
    triggers: List[str]  # List of trigger IDs that spawn this entity


@dataclass(slots=True)
class SpawnLocation:
    """A location where an entity can spawn."""

    tile_x: int  # X position in tiles
    tile_y: int  # Y position in tiles
    screen: int  # Screen index
    spec: SpawnSpec  # Spawn specification
    symbol: str  # Symbol used in layout

    @property
    def world_x(self) -> float:
        """Get world X position in pixels."""
        from ..constants import TILE_SIZE

        return self.tile_x * TILE_SIZE

    @property
    def world_y(self) -> float:
        """Get world Y position in pixels."""
        from ..constants import TILE_SIZE

        return self.tile_y * TILE_SIZE


@dataclass(slots=True)
class SpawnTrigger:
    """A camera-based trigger for spawning entities."""

    trigger_id: str  # Unique trigger identifier
    camera_x: float  # Camera X position that triggers this spawn
    screen: int  # Screen where trigger is located
    tile_x: int  # Tile column where trigger is located
    spawned: bool = False  # Whether this trigger has been activated

    def should_trigger(self, current_camera_x: float) -> bool:
        """Check if this trigger should activate based on camera position.

        Args:
            current_camera_x: Current camera X position

        Returns:
            True if trigger should activate
        """
        if self.spawned:
            return False
        return current_camera_x >= self.camera_x

    def reset(self) -> None:
        """Reset trigger to pending state."""
        self.spawned = False


@dataclass(slots=True)
class SpawnManager:
    """Manages spawn triggers and locations for a level."""

    locations: List[SpawnLocation] = field(default_factory=list)
    triggers: Dict[str, SpawnTrigger] = field(default_factory=dict)
    _pending_triggers: Set[str] = field(default_factory=set)

    def add_location(self, location: SpawnLocation) -> None:
        """Add a spawn location.

        Args:
            location: Spawn location to add
        """
        self.locations.append(location)

    def add_trigger(self, trigger: SpawnTrigger) -> None:
        """Add a spawn trigger.

        Args:
            trigger: Spawn trigger to add
        """
        self.triggers[trigger.trigger_id] = trigger
        self._pending_triggers.add(trigger.trigger_id)

    def get_locations_for_trigger(self, trigger_id: str) -> List[SpawnLocation]:
        """Get all spawn locations associated with a trigger.

        Args:
            trigger_id: Trigger identifier

        Returns:
            List of spawn locations for this trigger
        """
        return [loc for loc in self.locations if trigger_id in loc.spec.triggers]

    def check_triggers(self, camera_x: float) -> List[str]:
        """Check which triggers should activate based on camera position.

        Args:
            camera_x: Current camera X position

        Returns:
            List of trigger IDs that should activate
        """
        activated = []
        for trigger_id in list(self._pending_triggers):
            trigger = self.triggers[trigger_id]
            if trigger.should_trigger(camera_x):
                activated.append(trigger_id)
                trigger.spawned = True
                self._pending_triggers.remove(trigger_id)
        return activated

    def reset_all_triggers(self) -> None:
        """Reset all triggers to pending state."""
        for trigger in self.triggers.values():
            trigger.reset()
        self._pending_triggers = set(self.triggers.keys())
