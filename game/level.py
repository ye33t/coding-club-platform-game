"""Level data and tile management."""

from typing import List, Optional, Tuple

from .constants import BLOCK_SIZE, BLOCKS_HORIZONTAL, BLOCKS_VERTICAL
from .terrain import BounceBehavior, TerrainManager, VisualState
from .tile_definitions import TILE_BRICK_TOP, TileDefinition, get_tile_definition

# Tile types (imported from tile_definitions for consistency)
from .tile_definitions import (
    TILE_ARCH_CENTER,
    TILE_ARCH_LEFT,
    TILE_ARCH_RIGHT,
    TILE_BATTLEMENT,
    TILE_BEANSTALK,
    TILE_BLOCK,
    TILE_BLOCK_FLAT,
    TILE_BRICK,
    TILE_BRIDGE,
    TILE_CANNON_BOTTOM,
    TILE_CANNON_CENTER,
    TILE_CANNON_TOP,
    TILE_EARTH,
    TILE_EMPTY,
    TILE_GROUND,
    TILE_LADDER,
    TILE_PIPE_HORIZONTAL_BOTTOM,
    TILE_PIPE_HORIZONTAL_TOP,
    TILE_PIPE_JUNCTION_BOTTOM,
    TILE_PIPE_JUNCTION_TOP,
    TILE_PIPE_LEFT,
    TILE_PIPE_RIGHT,
    TILE_PIPE_TOP_LEFT,
    TILE_PIPE_TOP_RIGHT,
    TILE_ROCKS,
    TILE_SAND,
    TILE_VOID,
)


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

        # Initialize tile data (3D structure: screen -> y -> x)
        # tiles[screen][y][x] where y=0 is bottom of each screen
        # Each entry represents a 16x16 pixel block
        self.tiles: dict[int, List[List[int]]] = {}

        # Initialize terrain manager for tile behaviors
        self.terrain_manager = TerrainManager()

        # Create a simple test level
        self._create_test_level()

    def _create_test_level(self):
        """Create a simple test level with ground and some platforms across multiple screens."""
        # Initialize screens -1, 0, 1
        for screen_idx in [-1, 0, 1]:
            self.tiles[screen_idx] = []
            for y in range(self.height_tiles):
                row = [TILE_EMPTY] * self.width_tiles
                self.tiles[screen_idx].append(row)

        # Screen 0 (main screen)
        # Ground (bottom 2 rows)
        for x in range(self.width_tiles):
            self.tiles[0][0][x] = TILE_GROUND
            self.tiles[0][1][x] = TILE_GROUND

        # Add some gaps in the ground (only if wide enough)
        if self.width_tiles > 23:
            for x in range(20, 23):
                self.tiles[0][0][x] = TILE_EMPTY
                self.tiles[0][1][x] = TILE_EMPTY

        if self.width_tiles > 44:
            for x in range(40, 44):
                self.tiles[0][0][x] = TILE_EMPTY
                self.tiles[0][1][x] = TILE_EMPTY

        # Add some platforms (only if wide enough)
        # Platform 1
        if self.width_tiles > 15:
            for x in range(10, min(15, self.width_tiles)):
                self.tiles[0][6][x] = TILE_BRICK_TOP
                # Make this platform bounceable
                self.terrain_manager.set_tile_behavior(0, x, 6, BounceBehavior())

        # Platform 2
        if self.width_tiles > 25:
            for x in range(25, min(32, self.width_tiles)):
                self.tiles[0][8][x] = TILE_BRICK_TOP
                # Make this platform bounceable
                self.terrain_manager.set_tile_behavior(0, x, 8, BounceBehavior())

        # Add a pipe (2x3 tiles)
        if self.width_tiles > 35:
            # Top of pipe
            self.tiles[0][4][35] = TILE_PIPE_TOP_LEFT
            self.tiles[0][4][36] = TILE_PIPE_TOP_RIGHT
            # Body of pipe
            self.tiles[0][3][35] = TILE_PIPE_LEFT
            self.tiles[0][3][36] = TILE_PIPE_RIGHT
            self.tiles[0][2][35] = TILE_PIPE_LEFT
            self.tiles[0][2][36] = TILE_PIPE_RIGHT

        # Screen 1 (above main screen) - Sky area
        # Floating platforms
        for x in range(5, min(10, self.width_tiles)):
            self.tiles[1][4][x] = TILE_BRICK_TOP

        for x in range(15, min(20, self.width_tiles)):
            self.tiles[1][7][x] = TILE_BRICK_TOP

        # Screen -1 (below main screen) - Underground area
        # Full ground
        for x in range(self.width_tiles):
            self.tiles[-1][0][x] = TILE_GROUND
            self.tiles[-1][1][x] = TILE_GROUND
            self.tiles[-1][2][x] = TILE_GROUND

    def get_tile(self, screen: int, tile_x: int, tile_y: int) -> int:
        """Get tile type at given tile coordinates.

        Args:
            screen: Screen index
            tile_x: X position in tiles
            tile_y: Y position in tiles (0 = bottom of screen)

        Returns:
            Tile type, or TILE_EMPTY if out of bounds
        """
        if screen not in self.tiles:
            return TILE_EMPTY
        if tile_x < 0 or tile_x >= self.width_tiles:
            return TILE_EMPTY
        if tile_y < 0 or tile_y >= self.height_tiles:
            return TILE_EMPTY
        return self.tiles[screen][tile_y][tile_x]

    def get_tile_at_position(self, screen: int, world_x: float, world_y: float) -> int:
        """Get tile type at given world position.

        Args:
            screen: Screen index
            world_x: X position in world pixels
            world_y: Y position in screen-relative pixels (0-224, from bottom)

        Returns:
            Tile type at that position
        """
        tile_x = int(world_x // BLOCK_SIZE)
        tile_y = int(world_y // BLOCK_SIZE)
        return self.get_tile(screen, tile_x, tile_y)

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

    def get_visible_tiles(self, screen: int, camera_x: float) -> List[Tuple[int, int, int]]:
        """Get all tiles visible in the current camera view.

        Args:
            screen: Screen index
            camera_x: Camera position in world pixels

        Returns:
            List of (tile_x, tile_y, tile_type) for visible tiles on the specified screen
        """
        if screen not in self.tiles:
            return []

        # Calculate tile range visible on screen
        start_tile_x = max(0, int(camera_x // BLOCK_SIZE))
        end_tile_x = min(
            self.width_tiles,
            int((camera_x + BLOCKS_HORIZONTAL * BLOCK_SIZE) // BLOCK_SIZE) + 1,
        )

        visible_tiles = []
        for tile_y in range(self.height_tiles):
            for tile_x in range(start_tile_x, end_tile_x):
                tile_type = self.tiles[screen][tile_y][tile_x]
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

    def get_tile_visual_state(
        self, screen: int, tile_x: int, tile_y: int
    ) -> Optional[VisualState]:
        """Get visual state for rendering a tile.

        Args:
            screen: The screen index
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            VisualState if tile has behaviors, None otherwise
        """
        instance = self.terrain_manager.get_instance(screen, tile_x, tile_y)
        if instance and instance.state:
            return instance.state.visual
        return None

    def check_collision(
        self, screen: int, x: float, y: float, width: float, height: float
    ) -> Optional[str]:
        """Check if a rectangle collides with solid tiles.

        Args:
            screen: Screen index
            x: Left edge in world pixels
            y: Bottom edge in screen-relative pixels (0-224)
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
            if self.is_solid(self.get_tile(screen, tile_x, bottom_tile)):
                return "ground"

        # Check ceiling collision (top edge)
        for tile_x in range(left_tile, right_tile + 1):
            if self.is_solid(self.get_tile(screen, tile_x, top_tile)):
                return "ceiling"

        # Check left wall
        for tile_y in range(bottom_tile, top_tile + 1):
            if self.is_solid(self.get_tile(screen, left_tile, tile_y)):
                return "wall_left"

        # Check right wall
        for tile_y in range(bottom_tile, top_tile + 1):
            if self.is_solid(self.get_tile(screen, right_tile, tile_y)):
                return "wall_right"

        return None
