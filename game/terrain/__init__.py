"""Terrain behavior system for tile animations and effects."""

from .base import BehaviorContext, TerrainBehavior, TileEvent, TileState, VisualState
from .bounce import BounceBehavior
from .castle_exit import CastleExitBehavior
from .factory import BehaviorFactory, BehaviorFactoryError
from .flagpole import FlagpoleBehavior
from .item_box import ItemBoxBehavior, ItemBoxSpawnType
from .manager import TerrainManager
from .none import NoneBehavior
from .smash import SmashBehavior
from .warp import WarpBehavior

__all__ = [
    "BehaviorContext",
    "TerrainBehavior",
    "TileEvent",
    "TileState",
    "VisualState",
    "BounceBehavior",
    "CastleExitBehavior",
    "FlagpoleBehavior",
    "ItemBoxBehavior",
    "ItemBoxSpawnType",
    "NoneBehavior",
    "SmashBehavior",
    "WarpBehavior",
    "BehaviorFactory",
    "BehaviorFactoryError",
    "TerrainManager",
]
