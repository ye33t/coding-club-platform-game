"""Physics events that trigger state transitions or side effects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional

if TYPE_CHECKING:
    from ..effects.base import Effect, EffectFactory
    from ..entities.base import Entity
    from ..terrain.warp import WarpBehavior


class PhysicsEvent:
    """Base class for physics events emitted by the pipeline."""

    short_circuit: ClassVar[bool] = False


class DeathEvent(PhysicsEvent):
    """Mario fell off the screen."""

    short_circuit: ClassVar[bool] = True


@dataclass(slots=True)
class WarpEvent(PhysicsEvent):
    """Mario entered a warp pipe."""

    warp_behavior: "WarpBehavior"
    short_circuit: ClassVar[bool] = True


@dataclass(slots=True)
class EndLevelEvent(PhysicsEvent):
    """Mario touched the flagpole."""

    flagpole_x: float  # X pixel position (center of flagpole)
    flagpole_base_y: float  # Y pixel position of base block top
    short_circuit: ClassVar[bool] = True


@dataclass(slots=True)
class RemoveEntityEvent(PhysicsEvent):
    """Mark an entity for removal after the pipeline completes."""

    entity: "Entity"


@dataclass(slots=True)
class TerrainTileChangeEvent(PhysicsEvent):
    """Replace a tile and optionally attach a new behavior."""

    screen: int
    x: int
    y: int
    slug: str
    behavior_type: Optional[str] = None
    behavior_params: Optional[Dict[str, Any]] = None


@dataclass(slots=True)
class SpawnEffectEvent(PhysicsEvent):
    """Spawn a transient visual effect."""

    effect: "Effect | EffectFactory"


@dataclass(slots=True)
class SpawnEntityEvent(PhysicsEvent):
    """Spawn a game entity."""

    entity: "Entity"
