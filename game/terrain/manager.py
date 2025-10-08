"""Manager for terrain behaviors in a level."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState

if TYPE_CHECKING:
    from ..effects import Effect, EffectFactory, EffectManager
    from ..level import Level


@dataclass
class _TileChangeCommand:
    screen: int
    x: int
    y: int
    slug: str


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

    def __init__(self) -> None:
        """Initialize the terrain manager."""
        # Only store tiles that have behaviors
        self.instances: Dict[Tuple[int, int, int], TileInstance] = {}
        self._tile_change_commands: List[_TileChangeCommand] = []
        self._effect_commands: List["Effect | EffectFactory"] = []

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

    def queue_tile_change(self, screen: int, x: int, y: int, slug: str) -> None:
        """Request that a tile be replaced after the physics step."""

        self._tile_change_commands.append(_TileChangeCommand(screen, x, y, slug))

    def queue_effect(self, effect: "Effect | EffectFactory") -> None:
        """Request that an effect be spawned after the physics step."""

        self._effect_commands.append(effect)

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
                x,
                y,
                screen,
                instance.state,
                event,
                0,  # dt=0 for events
                self.queue_tile_change,
                self.queue_effect,
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
                    self.queue_tile_change,
                    self.queue_effect,
                )
                instance.behavior.process(context)

    def apply_pending_commands(
        self, level: "Level", effect_manager: Optional["EffectManager"] = None
    ) -> None:
        """Apply queued tile changes and spawn requested effects."""

        for command in self._tile_change_commands:
            level.set_terrain_tile(command.screen, command.x, command.y, command.slug)
            self.instances.pop((command.screen, command.x, command.y), None)
        self._tile_change_commands.clear()

        if effect_manager is not None:
            for effect in self._effect_commands:
                effect_manager.spawn(effect)
        self._effect_commands.clear()
