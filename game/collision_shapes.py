"""Collision shape definitions for tiles."""

from enum import Enum
from typing import Optional

from .constants import TILE_SIZE


class CollisionType(Enum):
    """Types of collision shapes for tiles."""

    EMPTY = "empty"  # No collision
    SOLID = "solid"  # Full rectangle collision
    SLOPE_UP = "slope_up"  # 45° slope ascending left to right
    SLOPE_DOWN = "slope_down"  # 45° slope descending left to right
    PLATFORM = "platform"  # One-way platform (can jump through from below)


class TileCollision:
    """Handles collision detection for different tile shapes."""

    # Map tile types to collision types
    TILE_COLLISIONS = {
        0: CollisionType.EMPTY,  # TILE_EMPTY
        1: CollisionType.SOLID,  # TILE_GROUND
        2: CollisionType.SOLID,  # TILE_BRICK
        3: CollisionType.SOLID,  # TILE_PIPE
        4: CollisionType.SLOPE_UP,  # TILE_SLOPE_UP
        5: CollisionType.SLOPE_DOWN,  # TILE_SLOPE_DOWN
    }

    @staticmethod
    def get_collision_type(tile_type: int) -> CollisionType:
        """Get the collision type for a tile.

        Args:
            tile_type: The tile type ID

        Returns:
            The collision type for this tile
        """
        return TileCollision.TILE_COLLISIONS.get(tile_type, CollisionType.EMPTY)

    @staticmethod
    def get_ground_height(tile_type: int, x_offset: float) -> Optional[float]:
        """Get the ground height at a specific X offset within a tile.

        Args:
            tile_type: The tile type ID
            x_offset: X position within the tile (0 to TILE_SIZE)

        Returns:
            Height from bottom of tile (0 to TILE_SIZE), or None if no ground
        """
        collision_type = TileCollision.get_collision_type(tile_type)

        if collision_type == CollisionType.EMPTY:
            return None

        elif collision_type == CollisionType.SOLID:
            # Full height across entire tile
            return TILE_SIZE

        elif collision_type == CollisionType.SLOPE_UP:
            # Linear interpolation from 0 to TILE_SIZE
            # At x=0: height=0, at x=TILE_SIZE: height=TILE_SIZE
            x_ratio = max(0, min(1, x_offset / TILE_SIZE))
            return x_ratio * TILE_SIZE

        elif collision_type == CollisionType.SLOPE_DOWN:
            # Linear interpolation from TILE_SIZE to 0
            # At x=0: height=TILE_SIZE, at x=TILE_SIZE: height=0
            x_ratio = max(0, min(1, x_offset / TILE_SIZE))
            return (1 - x_ratio) * TILE_SIZE

        elif collision_type == CollisionType.PLATFORM:
            # Platform has collision only at the top
            return TILE_SIZE

        return None

    @staticmethod
    def is_solid_at(tile_type: int, x_offset: float, y_offset: float) -> bool:
        """Check if a point within a tile is solid.

        Args:
            tile_type: The tile type ID
            x_offset: X position within the tile (0 to TILE_SIZE)
            y_offset: Y position within the tile from bottom (0 to TILE_SIZE)

        Returns:
            True if the point is inside solid material
        """
        ground_height = TileCollision.get_ground_height(tile_type, x_offset)

        if ground_height is None:
            return False

        # Point is solid if it's below the ground height
        return y_offset <= ground_height

    @staticmethod
    def is_one_way(tile_type: int) -> bool:
        """Check if a tile is a one-way platform.

        Args:
            tile_type: The tile type ID

        Returns:
            True if this is a one-way platform
        """
        return TileCollision.get_collision_type(tile_type) == CollisionType.PLATFORM

    @staticmethod
    def get_slope_normal(tile_type: int) -> tuple[float, float]:
        """Get the surface normal for a tile (for physics calculations).

        Args:
            tile_type: The tile type ID

        Returns:
            (nx, ny) normalized surface normal vector
        """
        collision_type = TileCollision.get_collision_type(tile_type)

        if collision_type == CollisionType.SLOPE_UP:
            # 45° slope up: normal points up-left
            # Normal is perpendicular to slope direction (1, 1)
            # So normal is (-1, 1) normalized
            import math

            return (-1 / math.sqrt(2), 1 / math.sqrt(2))

        elif collision_type == CollisionType.SLOPE_DOWN:
            # 45° slope down: normal points up-right
            # Normal is perpendicular to slope direction (1, -1)
            # So normal is (1, 1) normalized
            import math

            return (1 / math.sqrt(2), 1 / math.sqrt(2))

        else:
            # Default: normal points straight up
            return (0, 1)
