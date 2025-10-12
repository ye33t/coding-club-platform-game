"""Manager for terrain behaviors in a level."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional, Tuple

from ..physics.events import TerrainTileChangeEvent
from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState

if TYPE_CHECKING:
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

    def process_behaviors(self, dt: float, physics: "PhysicsContext") -> None:
        """Update all tile behaviors and allow them to emit events."""

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

    def apply_tile_change(self, event: TerrainTileChangeEvent, level: "Level") -> None:
        """Apply a tile change triggered by a physics event."""

        from .factory import BehaviorFactory

        level.set_terrain_tile(event.screen, event.x, event.y, event.slug)
        self.instances.pop((event.screen, event.x, event.y), None)

        if not event.behavior_type:
            return

        try:
            factory = BehaviorFactory()
            behavior = factory.create(event.behavior_type, event.behavior_params)
            self.set_tile_behavior(event.screen, event.x, event.y, behavior)
        except Exception as exc:  # pragma: no cover - best-effort logging
            print(  # noqa: T201
                f"Warning: Failed to create behavior '{event.behavior_type}': {exc}"
            )
