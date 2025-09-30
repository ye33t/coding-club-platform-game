"""Base classes for terrain behavior system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class TileEvent(Enum):
    """Events that can be triggered on tiles."""

    HIT_FROM_BELOW = "hit_from_below"


@dataclass
class VisualState:
    """Visual presentation state - what behaviors can modify."""

    offset_y: float = 0.0
    # offset_x, rotation, scale can be added later when needed


@dataclass
class TileState:
    """Container for all tile state."""

    visual: VisualState = field(default_factory=VisualState)
    data: Dict[str, float] = field(default_factory=dict)  # Behavior-specific storage


@dataclass
class BehaviorContext:
    """Context passed to behaviors for processing."""

    tile_x: int
    tile_y: int
    screen: int
    state: TileState
    event: Optional[TileEvent]
    dt: float


class TerrainBehavior(ABC):
    """Base class for all terrain behaviors."""

    @abstractmethod
    def process(self, context: BehaviorContext) -> None:
        """Process the behavior for this tile.

        Args:
            context: The context containing tile state and event info
        """
        pass