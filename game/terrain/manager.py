"""Manager for terrain behaviors in a level."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState

if TYPE_CHECKING:
    from ..effects import Effect, EffectFactory, EffectManager
    from ..entities import Entity, EntityManager
    from ..level import Level


@dataclass
class _TileChangeCommand:
    screen: int
    x: int
    y: int
    slug: str
    behavior_type: Optional[str] = None
    behavior_params: Optional[Dict[str, Any]] = None


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
        self._entity_commands: List["Entity"] = []

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

    def queue_tile_change(
        self,
        screen: int,
        x: int,
        y: int,
        slug: str,
        behavior_type: Optional[str] = None,
        behavior_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Request that a tile be replaced after the physics step.

        Args:
            screen: Screen index
            x: Tile X coordinate
            y: Tile Y coordinate
            slug: New tile visual slug
            behavior_type: Optional behavior type to attach to new tile
            behavior_params: Optional parameters for the behavior
        """

        self._tile_change_commands.append(
            _TileChangeCommand(screen, x, y, slug, behavior_type, behavior_params)
        )

    def queue_effect(self, effect: "Effect | EffectFactory") -> None:
        """Request that an effect be spawned after the physics step."""

        self._effect_commands.append(effect)

    def queue_entity(self, entity: "Entity") -> None:
        """Request that an entity be spawned after the physics step."""

        self._entity_commands.append(entity)

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
                self.queue_entity,
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
                    self.queue_entity,
                )
                instance.behavior.process(context)

    def apply_pending_commands(
        self,
        level: "Level",
        effect_manager: Optional["EffectManager"] = None,
        entity_manager: Optional["EntityManager"] = None,
    ) -> None:
        """Apply queued tile changes and spawn requested effects and entities."""

        from .factory import BehaviorFactory

        factory = BehaviorFactory()

        for command in self._tile_change_commands:
            # Change the tile visual
            level.set_terrain_tile(command.screen, command.x, command.y, command.slug)

            # Remove old behavior instance
            self.instances.pop((command.screen, command.x, command.y), None)

            # Create and attach new behavior if specified
            if command.behavior_type:
                try:
                    behavior = factory.create(
                        command.behavior_type, command.behavior_params
                    )
                    self.set_tile_behavior(
                        command.screen, command.x, command.y, behavior
                    )
                except Exception as e:
                    # Log error but don't crash - tile change still happened
                    print(
                        f"Warning: Failed to create behavior "
                        f"'{command.behavior_type}': {e}"
                    )

        self._tile_change_commands.clear()

        if effect_manager is not None:
            for effect in self._effect_commands:
                effect_manager.spawn(effect)
        self._effect_commands.clear()

        if entity_manager is not None:
            for entity in self._entity_commands:
                entity_manager.spawn(entity)
        self._entity_commands.clear()
