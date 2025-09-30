"""Manager for terrain behaviors in a level."""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState


@dataclass
class TileInstance:
    """Represents a tile with behavior."""

    x: int
    y: int
    screen: int
    state: TileState
    behavior: Optional[TerrainBehavior]  # Single behavior for now


class TerrainManager:
    """Manages all tiles with behaviors in a level."""

    def __init__(self):
        """Initialize the terrain manager."""
        # Only store tiles that have behaviors
        self.instances: Dict[Tuple[int, int, int], TileInstance] = {}

    def set_tile_behavior(
        self, screen: int, x: int, y: int, behavior: TerrainBehavior
    ) -> None:
        """Assign a behavior to a specific tile.

        Args:
            screen: The screen index
            x: Tile X coordinate
            y: Tile Y coordinate
            behavior: The behavior to assign
        """
        key = (screen, x, y)
        self.instances[key] = TileInstance(x, y, screen, TileState(), behavior)

    def get_instance(self, screen: int, x: int, y: int) -> Optional[TileInstance]:
        """Get tile instance if it exists.

        Args:
            screen: The screen index
            x: Tile X coordinate
            y: Tile Y coordinate

        Returns:
            TileInstance if exists, None otherwise
        """
        return self.instances.get((screen, x, y))

    def trigger_event(self, screen: int, x: int, y: int, event: TileEvent) -> None:
        """Trigger an event on a specific tile.

        Args:
            screen: The screen index
            x: Tile X coordinate
            y: Tile Y coordinate
            event: The event to trigger
        """
        instance = self.get_instance(screen, x, y)
        if instance and instance.behavior:
            context = BehaviorContext(
                x, y, screen, instance.state, event, 0  # dt=0 for events
            )
            instance.behavior.process(context)

    def update(self, dt: float) -> None:
        """Update all tile behaviors.

        Args:
            dt: Time delta since last update
        """
        for instance in self.instances.values():
            if instance.behavior:
                context = BehaviorContext(
                    instance.x,
                    instance.y,
                    instance.screen,
                    instance.state,
                    None,  # No event during updates
                    dt,
                )
                instance.behavior.process(context)