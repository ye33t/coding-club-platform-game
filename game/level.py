"""Level data and tile management."""

from typing import List, Optional, Tuple

from .constants import TILE_SIZE, TILES_HORIZONTAL, TILES_VERTICAL

# Tile types
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_BRICK = 2
TILE_PIPE = 3
TILE_SLOPE_UP = 4  # 45° slope ascending left to right
TILE_SLOPE_DOWN = 5  # 45° slope descending left to right


class Level:
    """Manages level geometry and tile data."""

    def __init__(self, width_in_screens: int = 2):
        """Initialize level with specified width.

        Args:
            width_in_screens: Level width in screen units (each screen = 32 tiles)
        """
        self.width_tiles = width_in_screens * TILES_HORIZONTAL
        self.height_tiles = TILES_VERTICAL
        self.width_pixels = self.width_tiles * TILE_SIZE
        self.height_pixels = self.height_tiles * TILE_SIZE

        # Initialize tile data (2D array)
        # tiles[y][x] where y=0 is bottom of screen
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

        # Add slopes (creating a hill)
        # Slope up
        self.tiles[2][45] = TILE_SLOPE_UP
        self.tiles[3][46] = TILE_SLOPE_UP
        self.tiles[4][47] = TILE_SLOPE_UP

        # Flat top
        for x in range(48, 52):
            self.tiles[5][x] = TILE_GROUND

        # Slope down
        self.tiles[4][52] = TILE_SLOPE_DOWN
        self.tiles[3][53] = TILE_SLOPE_DOWN
        self.tiles[2][54] = TILE_SLOPE_DOWN

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
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)
        return self.get_tile(tile_x, tile_y)

    def is_solid(self, tile_type: int) -> bool:
        """Check if a tile type is solid (blocks movement).

        Args:
            tile_type: The tile type to check

        Returns:
            True if tile blocks movement
        """
        return tile_type in [
            TILE_GROUND,
            TILE_BRICK,
            TILE_PIPE,
            TILE_SLOPE_UP,
            TILE_SLOPE_DOWN,
        ]

    def get_visible_tiles(self, camera_x: float) -> List[Tuple[int, int, int]]:
        """Get all tiles visible in the current camera view.

        Args:
            camera_x: Camera position in world pixels

        Returns:
            List of (tile_x, tile_y, tile_type) for visible tiles
        """
        # Calculate tile range visible on screen
        start_tile_x = max(0, int(camera_x // TILE_SIZE))
        end_tile_x = min(
            self.width_tiles,
            int((camera_x + TILES_HORIZONTAL * TILE_SIZE) // TILE_SIZE) + 1,
        )

        visible_tiles = []
        for tile_y in range(self.height_tiles):
            for tile_x in range(start_tile_x, end_tile_x):
                tile_type = self.tiles[tile_y][tile_x]
                if tile_type != TILE_EMPTY:
                    visible_tiles.append((tile_x, tile_y, tile_type))

        return visible_tiles

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
        left_tile = int(x // TILE_SIZE)
        right_tile = int((x + width - 1) // TILE_SIZE)
        bottom_tile = int(y // TILE_SIZE)
        top_tile = int((y + height - 1) // TILE_SIZE)

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
