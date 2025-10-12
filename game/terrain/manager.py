"""Manager for terrain behaviors in a level."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

from ..physics.events import (
    PhysicsEvent,
    SpawnEffectEvent,
    SpawnEntityEvent,
    TerrainTileChangeEvent,
)
from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState

if TYPE_CHECKING:
    from ..effects import Effect, EffectFactory, EffectManager
    from ..entities import Entity, EntityManager
    from ..level import Level


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
        self._pending_events: List[PhysicsEvent] = []
        self._event_emitter: Optional[Callable[[PhysicsEvent], None]] = None

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

    def _emit_event(self, event: PhysicsEvent) -> None:
        if self._event_emitter is not None:
            self._event_emitter(event)
        else:
            self._pending_events.append(event)

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

        event = TerrainTileChangeEvent(
            screen=screen,
            x=x,
            y=y,
            slug=slug,
            behavior_type=behavior_type,
            behavior_params=behavior_params,
        )
        self._emit_event(event)

    def queue_effect(self, effect: "Effect | EffectFactory") -> None:
        """Request that an effect be spawned after the physics step."""

        self._emit_event(SpawnEffectEvent(effect=effect))

    def queue_entity(self, entity: "Entity") -> None:
        """Request that an entity be spawned after the physics step."""

        self._emit_event(SpawnEntityEvent(entity=entity))

    def trigger_event(
        self,
        screen: int,
        x: int,
        y: int,
        event: TileEvent,
        emit_event: Optional[Callable[[PhysicsEvent], None]] = None,
    ) -> None:
        """Trigger an event on a specific tile.

        Args:
            screen: The screen index
            x: Tile X coordinate
            y: Tile Y coordinate
            event: The event to trigger
            emit_event: Optional callback to forward generated physics events
        """
        previous_emitter = self._event_emitter
        self._event_emitter = emit_event
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
        self._event_emitter = previous_emitter

    def update(
        self,
        dt: float,
        emit_event: Optional[Callable[[PhysicsEvent], None]] = None,
    ) -> None:
        """Update all tile behaviors.


        Args:
            dt: Time delta since last update
        """
        previous_emitter = self._event_emitter
        self._event_emitter = emit_event
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
        self._event_emitter = previous_emitter

    def drain_pending_events(self) -> List[PhysicsEvent]:
        """Retrieve and clear any pending terrain events."""
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def process_events(
        self,
        events: List[PhysicsEvent],
        level: "Level",
        effect_manager: Optional["EffectManager"] = None,
        entity_manager: Optional["EntityManager"] = None,
    ) -> None:
        """Apply terrain-related physics events."""

        from .factory import BehaviorFactory

        factory: Optional[BehaviorFactory] = None

        for event in events:
            if isinstance(event, TerrainTileChangeEvent):
                level.set_terrain_tile(event.screen, event.x, event.y, event.slug)
                self.instances.pop((event.screen, event.x, event.y), None)

                if event.behavior_type:
                    try:
                        if factory is None:
                            factory = BehaviorFactory()
                        behavior = factory.create(
                            event.behavior_type, event.behavior_params
                        )
                        self.set_tile_behavior(event.screen, event.x, event.y, behavior)
                    except Exception as exc:
                        print(
                            f"Warning: Failed to create behavior "
                            f"'{event.behavior_type}': {exc}"
                        )
            elif isinstance(event, SpawnEffectEvent):
                if effect_manager is not None:
                    effect_manager.spawn(event.effect)
            elif isinstance(event, SpawnEntityEvent):
                if entity_manager is not None:
                    entity_manager.spawn(event.entity)

    def apply_pending_commands(
        self,
        level: "Level",
        effect_manager: Optional["EffectManager"] = None,
        entity_manager: Optional["EntityManager"] = None,
    ) -> None:
        """Apply any pending events that were queued without an emitter."""
        events = self.drain_pending_events()
        if events:
            self.process_events(events, level, effect_manager, entity_manager)
