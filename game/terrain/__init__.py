"""Terrain behavior system for tile animations and effects."""

from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState, VisualState
from .bounce import BounceBehavior
from .factory import BehaviorFactory, BehaviorFactoryError
from .manager import TerrainManager

__all__ = [
    "BehaviorContext",
    "TerrainBehavior",
    "TileEvent",
    "TileState",
    "VisualState",
    "BounceBehavior",
    "BehaviorFactory",
    "BehaviorFactoryError",
    "TerrainManager",
]
