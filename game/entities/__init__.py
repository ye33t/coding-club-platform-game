"""Game entities (enemies and collectibles)."""

from .base import CollisionResponse, Entity, EntityState
from .manager import EntityManager
from .mushroom import MushroomEntity

__all__ = [
    "Entity",
    "EntityState",
    "CollisionResponse",
    "EntityManager",
    "MushroomEntity",
]
