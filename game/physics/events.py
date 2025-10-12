"""Physics events that trigger state transitions or side effects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
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
