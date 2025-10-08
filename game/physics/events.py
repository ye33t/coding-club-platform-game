"""Physics events that trigger state transitions."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..terrain.warp import WarpBehavior


class PhysicsEvent:
    """Base class for physics events that trigger state transitions."""

    pass


@dataclass
class DeathEvent(PhysicsEvent):
    """Mario fell off the screen."""

    pass


@dataclass
class WarpEvent(PhysicsEvent):
    """Mario entered a warp pipe."""

    warp_behavior: "WarpBehavior"


@dataclass
class EndLevelEvent(PhysicsEvent):
    """Mario touched the flagpole."""

    flagpole_x: float  # X pixel position (center of flagpole)
    flagpole_base_y: float  # Y pixel position of base block top
