"""Manager for terrain behaviors in a level."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from ..physics.events import (
    PhysicsEvent,
    SpawnEffectEvent,
    SpawnEntityEvent,
    TerrainTileChangeEvent,
)
from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState

if TYPE_CHECKING:
    from ..effects import EffectManager
    from ..entities import EntityManager
    from ..level import Level
    from ..physics.base import PhysicsContext


@dataclass
class TileInstance:
    """Represents a tile with behavior."""

    x: int
    y: int
    screen: int
    state: TileState
    behavior: Optional[TerrainBehavior]


class TerrainManager:
    """Manages all tiles with behaviors in a level."""

    def __init__(self) -> None:
        self.instances: Dict[Tuple[int, int, int], TileInstance] = {}

    def set_tile_behavior(
        self, screen: int, x: int, y: int, behavior: TerrainBehavior
    ) -> None:
        """Assign a behavior to a specific tile."""

        key = (screen, x, y)
        self.instances[key] = TileInstance(x, y, screen, TileState(), behavior)

    def get_instance(self, screen: int, x: int, y: int) -> Optional[TileInstance]:
        """Get tile instance if it exists."""

        return self.instances.get((screen, x, y))

    def trigger_event(
        self,
        screen: int,
        x: int,
        y: int,
        event: TileEvent,
        physics: "PhysicsContext",
    ) -> None:
        """Trigger an event on a specific tile."""

        instance = self.get_instance(screen, x, y)
        if not instance or not instance.behavior:
            return

        context = BehaviorContext(
            tile_x=x,
            tile_y=y,
            screen=screen,
            state=instance.state,
            event=event,
            dt=0.0,
            physics=physics,
        )
        instance.behavior.process(context)

    def update(self, dt: float, physics: "PhysicsContext") -> None:
        """Update all tile behaviors."""

        for instance in self.instances.values():
            if instance.behavior is None:
                continue

            context = BehaviorContext(
                tile_x=instance.x,
                tile_y=instance.y,
                screen=instance.screen,
                state=instance.state,
                event=None,
                dt=dt,
                physics=physics,
            )
            instance.behavior.process(context)

    def process_events(
        self,
        events: List[PhysicsEvent],
        level: "Level",
        effect_manager: Optional["EffectManager"] = None,
        entity_manager: Optional["EntityManager"] = None,
    ) -> None:
        """Apply terrain-related physics events."""

        from .factory import BehaviorFactory

        behavior_factory: Optional[BehaviorFactory] = None

        for event in events:
            if isinstance(event, TerrainTileChangeEvent):
                level.set_terrain_tile(event.screen, event.x, event.y, event.slug)
                self.instances.pop((event.screen, event.x, event.y), None)

                if event.behavior_type:
                    try:
                        if behavior_factory is None:
                            behavior_factory = BehaviorFactory()
                        behavior = behavior_factory.create(
                            event.behavior_type, event.behavior_params
                        )
                        self.set_tile_behavior(event.screen, event.x, event.y, behavior)
                    except Exception as exc:  # pragma: no cover - best-effort logging
                        print(  # noqa: T201
                            f"Warning: Failed to create behavior "
                            f"'{event.behavior_type}': {exc}"
                        )
            elif isinstance(event, SpawnEffectEvent):
                if effect_manager is not None:
                    effect_manager.spawn(event.effect)
            elif isinstance(event, SpawnEntityEvent):
                if entity_manager is not None:
                    entity_manager.spawn(event.entity)
