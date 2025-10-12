"""Spawn system data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple


@dataclass(slots=True)
class EntitySpec:
    """Specification for spawning an entity."""

    entity_type: str  # e.g., "goomba", "mushroom"
    params: Dict[str, Any]  # Entity-specific parameters like facing direction
    symbol: str  # Symbol used in layout to place this entity
    locations: List[Tuple[int, int, int]] = field(
        default_factory=list
    )  # (tile_x, tile_y, screen) tuples


@dataclass(slots=True)
class SpawnTrigger:
    """A camera-based trigger for spawning entities."""

    trigger_id: str  # Unique trigger identifier
    camera_x: float  # Camera X position that triggers this spawn
    screen: int  # Screen where trigger is located
    tile_x: int  # Tile column where trigger is located
    entities: List[EntitySpec] = field(default_factory=list)  # Entities to spawn
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
    """Manages spawn triggers for a level.

    Triggers are keyed by (screen, trigger_id) to avoid clobbering entries that
    reuse identifiers across different screens.
    """

    triggers: Dict[Tuple[int, str], SpawnTrigger] = field(default_factory=dict)
    _pending_triggers: Set[Tuple[int, str]] = field(default_factory=set)

    def add_trigger(self, trigger: SpawnTrigger) -> None:
        """Add a spawn trigger.

        Args:
            trigger: Spawn trigger to add
        """
        trigger_key = (trigger.screen, trigger.trigger_id)
        if trigger_key in self.triggers:
            raise ValueError(
                f"Duplicate trigger '{trigger.trigger_id}' on screen {trigger.screen}"
            )
        self.triggers[trigger_key] = trigger
        self._pending_triggers.add(trigger_key)

    def check_triggers(self, camera_x: float) -> List[SpawnTrigger]:
        """Check which triggers should activate based on camera position.

        Args:
            camera_x: Current camera X position

        Returns:
            List of triggers that should activate
        """
        activated: List[SpawnTrigger] = []
        for trigger_key in list(self._pending_triggers):
            trigger = self.triggers[trigger_key]
            if trigger.should_trigger(camera_x):
                activated.append(trigger)
                trigger.spawned = True
                self._pending_triggers.remove(trigger_key)
        return activated

    def reset_all_triggers(self) -> None:
        """Reset all triggers to pending state."""
        for trigger in self.triggers.values():
            trigger.reset()
        self._pending_triggers = set(self.triggers.keys())
