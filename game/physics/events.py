"""Physics events that trigger state transitions or side effects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional

if TYPE_CHECKING:
    from ..effects.base import Effect, EffectFactory
    from ..entities.base import Entity
    from ..terrain.warp import WarpBehavior
    from ..world import World
    from .base import PhysicsContext

from ..score import ScoreType


class PhysicsEvent(ABC):
    """Base class for physics events emitted by the pipeline."""

    short_circuit: ClassVar[bool] = False

    @abstractmethod
    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        """Apply the event to the world and return True to short-circuit."""


class DeathEvent(PhysicsEvent):
    """Mario fell off the screen."""

    short_circuit: ClassVar[bool] = True

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        return True


@dataclass(slots=True)
class WarpEvent(PhysicsEvent):
    """Mario entered a warp pipe."""

    warp_behavior: "WarpBehavior"
    short_circuit: ClassVar[bool] = True

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        return True


@dataclass(slots=True)
class EndLevelEvent(PhysicsEvent):
    """Mario touched the flagpole."""

    flagpole_x: float  # X pixel position (center of flagpole)
    flagpole_base_y: float  # Y pixel position of base block top
    short_circuit: ClassVar[bool] = True

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        return True


@dataclass(slots=True)
class RemoveEntityEvent(PhysicsEvent):
    """Mark an entity for removal after the pipeline completes."""

    entity: "Entity"

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        world.entities.remove(self.entity)
        return False


@dataclass(slots=True)
class TerrainTileChangeEvent(PhysicsEvent):
    """Replace a tile and optionally attach a new behavior."""

    screen: int
    x: int
    y: int
    slug: str
    behavior_type: Optional[str] = None
    behavior_params: Optional[Dict[str, Any]] = None

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        world.level.terrain_manager.apply_tile_change(self, world.level)
        return False


@dataclass(slots=True)
class SpawnEffectEvent(PhysicsEvent):
    """Spawn a transient visual effect."""

    effect: "Effect | EffectFactory"

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        world.effects.spawn(self.effect)
        return False


@dataclass(slots=True)
class SpawnEntityEvent(PhysicsEvent):
    """Spawn a game entity."""

    entity: "Entity"

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        world.entities.spawn(self.entity)
        return False


@dataclass(slots=True)
class AwardScoreEvent(PhysicsEvent):
    """Increment the global score."""

    amount: int

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        world.award_score(self.amount)
        return False


@dataclass(slots=True)
class CollectCoinEvent(PhysicsEvent):
    """Increment the coin counter and associated score."""

    amount: int = 1

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        world.collect_coin(self.amount)
        return False


@dataclass(slots=True)
class EnemyScoreEvent(PhysicsEvent):
    """Apply combo-based scoring for enemy defeats."""

    score_type: ScoreType
    source_entity: "Entity | None" = None
    position: tuple[float, float] | None = None

    def dispatch(self, world: "World", context: "PhysicsContext") -> bool:
        world.handle_enemy_score(
            self.score_type,
            source=self.source_entity,
            position=self.position,
        )
        return False
