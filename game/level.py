"""Level data and tile management."""

from typing import List, Optional, Tuple

from .constants import BLOCK_SIZE, BLOCKS_HORIZONTAL, BLOCKS_VERTICAL
from .tile_definitions import TileDefinition, get_tile_definition

# Tile types (imported from tile_definitions for consistency)
from .tile_definitions import TILE_BRICK, TILE_EMPTY, TILE_GROUND, TILE_PIPE


class Level:
    """Manages level geometry and tile data.

    Note: The level grid represents game blocks (16x16 pixels each),
    not individual NES tiles (8x8 pixels). Each block is a 2x2 tile sprite.
    """

    def __init__(self, width_in_screens: int = 2):
        """Initialize level with specified width.

        Args:
            width_in_screens: Level width in screen units (each screen = 16 blocks)
        """
        self.width_tiles = width_in_screens * BLOCKS_HORIZONTAL
        self.height_tiles = BLOCKS_VERTICAL
        self.width_pixels = self.width_tiles * BLOCK_SIZE
        self.height_pixels = self.height_tiles * BLOCK_SIZE

        # Initialize tile data (2D array)
        # tiles[y][x] where y=0 is bottom of screen
        # Each entry represents a 16x16 pixel block
        self.tiles: List[List[int]] = []
        for y in range(self.height_tiles):
            row = [TILE_EMPTY] * self.width_tiles
            self.tiles.append(row)

        # Create a simple test level
        self._create_test_level()

    def _create_test_level(self):
        """Create a simple test level with ground and some platforms."""
        # Ground (bottom 2 rows)
        for x in range(self.width_tiles):
            self.tiles[0][x] = TILE_GROUND
            self.tiles[1][x] = TILE_GROUND

        # Add some gaps in the ground
        for x in range(20, 23):
            self.tiles[0][x] = TILE_EMPTY
            self.tiles[1][x] = TILE_EMPTY

        for x in range(40, 44):
            self.tiles[0][x] = TILE_EMPTY
            self.tiles[1][x] = TILE_EMPTY

        # Add some platforms
        # Platform 1
        for x in range(10, 15):
            self.tiles[6][x] = TILE_BRICK

        # Platform 2
        for x in range(25, 32):
            self.tiles[8][x] = TILE_BRICK

    def get_tile(self, tile_x: int, tile_y: int) -> int:
        """Get tile type at given tile coordinates.

        Args:
            tile_x: X position in tiles
            tile_y: Y position in tiles (0 = bottom)

        Returns:
            Tile type, or TILE_EMPTY if out of bounds
        """
        if tile_x < 0 or tile_x >= self.width_tiles:
            return TILE_EMPTY
        if tile_y < 0 or tile_y >= self.height_tiles:
            return TILE_EMPTY
        return self.tiles[tile_y][tile_x]

    def get_tile_at_position(self, world_x: float, world_y: float) -> int:
        """Get tile type at given world position.

        Args:
            world_x: X position in world pixels
            world_y: Y position in world pixels (from bottom)

        Returns:
            Tile type at that position
        """
        tile_x = int(world_x // BLOCK_SIZE)
        tile_y = int(world_y // BLOCK_SIZE)
        return self.get_tile(tile_x, tile_y)

    def is_solid(self, tile_type: int) -> bool:
        """Check if a tile type has any solid quadrants.

        Args:
            tile_type: The tile type to check

        Returns:
            True if tile has any solid collision
        """
        tile_def = self.get_tile_definition(tile_type)
        if not tile_def:
            return False
        return tile_def["collision_mask"] != 0

    def get_visible_tiles(self, camera_x: float) -> List[Tuple[int, int, int]]:
        """Get all tiles visible in the current camera view.

        Args:
            camera_x: Camera position in world pixels

        Returns:
            List of (tile_x, tile_y, tile_type) for visible tiles
        """
        # Calculate tile range visible on screen
        start_tile_x = max(0, int(camera_x // BLOCK_SIZE))
        end_tile_x = min(
            self.width_tiles,
            int((camera_x + BLOCKS_HORIZONTAL * BLOCK_SIZE) // BLOCK_SIZE) + 1,
        )

        visible_tiles = []
        for tile_y in range(self.height_tiles):
            for tile_x in range(start_tile_x, end_tile_x):
                tile_type = self.tiles[tile_y][tile_x]
                if tile_type != TILE_EMPTY:
                    visible_tiles.append((tile_x, tile_y, tile_type))

        return visible_tiles

    def get_tile_definition(self, tile_type: int) -> Optional[TileDefinition]:
        """Get the definition for a tile type.

        Args:
            tile_type: The tile type ID

        Returns:
            TileDefinition for this tile, or None if not found
        """
        return get_tile_definition(tile_type)

    def check_collision(
        self, x: float, y: float, width: float, height: float
    ) -> Optional[str]:
        """Check if a rectangle collides with solid tiles.

        Args:
            x: Left edge in world pixels
            y: Bottom edge in world pixels
            width: Width in pixels
            height: Height in pixels

        Returns:
            Collision type ('ground', 'ceiling', 'wall_left', 'wall_right') or None
        """
        # Check corners and edges for collisions
        # Convert to tile coordinates
        left_tile = int(x // BLOCK_SIZE)
        right_tile = int((x + width - 1) // BLOCK_SIZE)
        bottom_tile = int(y // BLOCK_SIZE)
        top_tile = int((y + height - 1) // BLOCK_SIZE)

        # Check ground collision (bottom edge)
        for tile_x in range(left_tile, right_tile + 1):
            if self.is_solid(self.get_tile(tile_x, bottom_tile)):
                return "ground"

        # Check ceiling collision (top edge)
        for tile_x in range(left_tile, right_tile + 1):
            if self.is_solid(self.get_tile(tile_x, top_tile)):
                return "ceiling"

        # Check left wall
        for tile_y in range(bottom_tile, top_tile + 1):
            if self.is_solid(self.get_tile(left_tile, tile_y)):
                return "wall_left"

        # Check right wall
        for tile_y in range(bottom_tile, top_tile + 1):
            if self.is_solid(self.get_tile(right_tile, tile_y)):
                return "wall_right"

        return None
