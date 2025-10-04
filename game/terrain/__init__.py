"""Terrain behavior system for tile animations and effects."""

from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState, VisualState
from .bounce import BounceBehavior
from .factory import BehaviorFactory, BehaviorFactoryError
from .manager import TerrainManager
from .none import NoneBehavior
from .warp import WarpBehavior

__all__ = [
    "BehaviorContext",
    "TerrainBehavior",
    "TileEvent",
    "TileState",
    "VisualState",
    "BounceBehavior",
    "NoneBehavior",
    "WarpBehavior",
    "BehaviorFactory",
    "BehaviorFactoryError",
    "TerrainManager",
]
