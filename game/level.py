"""Level data and tile management."""

from typing import List, Optional, Tuple

from .constants import TILE_SIZE, TILES_HORIZONTAL
from .terrain import TerrainManager, VisualState
from .tile_definitions import TILE_EMPTY, TileDefinition, get_tile_definition


class Level:
    """Manages level geometry and tile data.

    Note: The level grid represents game tiles (16x16 pixels each),
    not individual NES sub-tiles (8x8 pixels). Each tile is a 2x2 sub-tile sprite.
    """

    def __init__(self):
        """Initialize an empty level.

        The level will be populated by a loader after construction.
        """
        self.width_tiles = 0
        self.height_tiles = 0
        self.width_pixels = 0
        self.height_pixels = 0

        # Spawn point (in tile coordinates)
        self.spawn_tile_x: int = 0
        self.spawn_tile_y: int = 0
        self.spawn_screen: int = 0

        # Initialize tile data (3D structure: screen -> y -> x)
        # tiles[screen][y][x] where y=0 is bottom of each screen
        # Each entry represents a 16x16 pixel tile
        self.tiles: dict[int, List[List[int]]] = {}

        # Initialize terrain manager for tile behaviors
        self.terrain_manager = TerrainManager()

    @property
    def spawn_x(self) -> float:
        """Get spawn X position in pixels."""
        return self.spawn_tile_x * TILE_SIZE

    @property
    def spawn_y(self) -> float:
        """Get spawn Y position in pixels."""
        return self.spawn_tile_y * TILE_SIZE

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
            raise ValueError(f"Screen {screen} not found in level data")
        if tile_x < 0 or tile_x >= self.width_tiles:
            raise ValueError(f"Tile X {tile_x} out of bounds")
        if tile_y < 0 or tile_y >= self.height_tiles:
            raise ValueError(f"Tile Y {tile_y} out of bounds")
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
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)
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
            raise ValueError(f"Tile definition for type {tile_type} not found")
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
            raise ValueError(f"Screen {screen} not found in level data")

        # Calculate tile range visible on screen
        start_tile_x = max(0, int(camera_x // TILE_SIZE))
        end_tile_x = min(
            self.width_tiles,
            int((camera_x + TILES_HORIZONTAL * TILE_SIZE) // TILE_SIZE) + 1,
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
        left_tile = int(x // TILE_SIZE)
        right_tile = int((x + width - 1) // TILE_SIZE)
        bottom_tile = int(y // TILE_SIZE)
        top_tile = int((y + height - 1) // TILE_SIZE)

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
