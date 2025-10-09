"""Level data and tile management."""

from typing import Dict, List, Optional, Tuple, cast

from .constants import TILE_SIZE, TILES_HORIZONTAL
from .content.tile_definitions import (
    TileDefinition,
    empty_tile_slug,
    get_tile_definition,
)
from .terrain import TerrainManager, VisualState


class Level:
    """Manages level geometry and tile data.

    Note: The level grid represents game tiles (16x16 pixels each),
    not individual NES sub-tiles (8x8 pixels). Each tile is a 2x2 sub-tile sprite.
    """

    def __init__(self) -> None:
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

        # Tile slug used for empty space
        self._empty_tile = empty_tile_slug()

        # Initialize terrain tile data (3D structure: screen -> y -> x)
        # terrain_tiles[screen][y][x] where y=0 is bottom of each screen
        # Each entry represents a 16x16 pixel terrain tile
        self.terrain_tiles: dict[int, List[List[str]]] = {}
        self._original_terrain_tiles: dict[int, List[List[str]]] = {}
        self._behavior_specs: dict[
            int, Dict[Tuple[int, int], Tuple[str, Dict[str, object]]]
        ] = {}

        # Initialize background tile data (screen -> y -> x)
        self.background_tiles: dict[int, List[List[str]]] = {}

        # Initialize zones data (3D structure: screen -> y -> x)
        # zones[screen][y][x] contains zone character (or '.' for no zone)
        self.zones: dict[int, List[List[str]]] = {}

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

    def get_background_tile(self, screen: int, tile_x: int, tile_y: int) -> str:
        """Get background tile type at given tile coordinates.

        Args:
            screen: Screen index
            tile_x: X position in tiles
            tile_y: Y position in tiles (0 = bottom of screen)

        Returns:
            Tile type, or TILE_EMPTY if out of bounds or no background
        """
        tiles = self.background_tiles.get(screen)
        if tiles is None:
            return self._empty_tile
        if tile_x < 0 or tile_x >= self.width_tiles:
            return self._empty_tile
        if tile_y < 0 or tile_y >= self.height_tiles:
            return self._empty_tile
        return cast(str, tiles[tile_y][tile_x])

    def get_visible_background_tiles(
        self, screen: int, camera_x: float
    ) -> List[Tuple[int, int, str]]:
        """Get background tiles visible in the current camera view.

        Args:
            screen: Screen index
            camera_x: Camera position in world pixels

        Returns:
            List of (tile_x, tile_y, tile_type) for background tiles within the view
        """
        tiles = self.background_tiles.get(screen)
        if tiles is None:
            return []

        # Calculate tile range visible on screen
        start_tile_x = max(0, int(camera_x // TILE_SIZE))
        end_tile_x = min(
            self.width_tiles,
            int((camera_x + TILES_HORIZONTAL * TILE_SIZE) // TILE_SIZE) + 1,
        )

        visible_tiles = []
        for tile_y in range(self.height_tiles):
            for tile_x in range(start_tile_x, end_tile_x):
                tile_type = tiles[tile_y][tile_x]
                if tile_type != self._empty_tile:
                    visible_tiles.append((tile_x, tile_y, tile_type))

        return visible_tiles

    def get_terrain_tile(self, screen: int, tile_x: int, tile_y: int) -> str:
        """Get terrain tile type at given tile coordinates.

        Args:
            screen: Screen index
            tile_x: X position in tiles
            tile_y: Y position in tiles (0 = bottom of screen)

        Returns:
            Tile type, or TILE_EMPTY if out of bounds
        """
        if screen not in self.terrain_tiles:
            raise ValueError(f"Screen {screen} not found in level data")
        if tile_x < 0 or tile_x >= self.width_tiles:
            return self._empty_tile
        if tile_y < 0 or tile_y >= self.height_tiles:
            return self._empty_tile
        return cast(str, self.terrain_tiles[screen][tile_y][tile_x])

    def set_terrain_tile(
        self, screen: int, tile_x: int, tile_y: int, tile_slug: str
    ) -> None:
        """Replace a terrain tile with a new slug."""

        if screen not in self.terrain_tiles:
            raise ValueError(f"Screen {screen} not found in level data")
        if tile_y < 0 or tile_y >= len(self.terrain_tiles[screen]):
            raise ValueError(f"Tile Y {tile_y} out of bounds")
        row = self.terrain_tiles[screen][tile_y]
        if tile_x < 0 or tile_x >= len(row):
            raise ValueError(f"Tile X {tile_x} out of bounds")
        row[tile_x] = tile_slug

    def register_behavior_spec(
        self,
        screen: int,
        tile_x: int,
        tile_y: int,
        behavior_type: str,
        params: Dict[str, object],
    ) -> None:
        """Record behavior configuration for later resets."""

        specs = self._behavior_specs.setdefault(screen, {})
        specs[(tile_x, tile_y)] = (behavior_type, dict(params))

    def snapshot_terrain(self) -> None:
        """Capture the current terrain layout for future resets."""

        self._original_terrain_tiles = {
            screen: [row[:] for row in rows]
            for screen, rows in self.terrain_tiles.items()
        }

    def reset_terrain(self) -> None:
        """Restore terrain tiles and behaviors to the last snapshot."""

        if not self._original_terrain_tiles:
            return
        self.terrain_tiles = {
            screen: [row[:] for row in rows]
            for screen, rows in self._original_terrain_tiles.items()
        }
        self.terrain_manager.instances.clear()

        if not self._behavior_specs:
            return

        from .terrain.factory import BehaviorFactory

        factory = BehaviorFactory()
        for screen, specs in self._behavior_specs.items():
            for (tile_x, tile_y), (behavior_type, params) in specs.items():
                behavior = factory.create(behavior_type, params or None)
                self.terrain_manager.set_tile_behavior(screen, tile_x, tile_y, behavior)

    def get_terrain_tile_at_position(
        self, screen: int, world_x: float, world_y: float
    ) -> str:
        """Get terrain tile type at given world position.

        Args:
            screen: Screen index
            world_x: X position in world pixels
            world_y: Y position in screen-relative pixels (0-224, from bottom)

        Returns:
            Tile type at that position
        """
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)
        return self.get_terrain_tile(screen, tile_x, tile_y)

    def is_solid(self, tile_type: str) -> bool:
        """Check if a tile type has any solid quadrants.

        Args:
            tile_type: The tile type to check

        Returns:
            True if tile has any solid collision
        """
        tile_def = self.get_tile_definition(tile_type)
        if not tile_def:
            raise ValueError(f"Tile definition for slug {tile_type!r} not found")
        return tile_def.collision_mask != 0

    def get_visible_terrain_tiles(
        self, screen: int, camera_x: float
    ) -> List[Tuple[int, int, str]]:
        """Get all terrain tiles visible in the current camera view.

        Args:
            screen: Screen index
            camera_x: Camera position in world pixels

        Returns:
            List of (tile_x, tile_y, tile_type) for tiles within the current view
        """
        if screen not in self.terrain_tiles:
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
                tile_type = self.terrain_tiles[screen][tile_y][tile_x]
                if tile_type != self._empty_tile:
                    visible_tiles.append((tile_x, tile_y, tile_type))

        return visible_tiles

    def get_tile_definition(self, tile_type: str) -> Optional[TileDefinition]:
        """Get the definition for a tile type.

        Args:
            tile_type: The tile type ID

        Returns:
            TileDefinition for this tile, or None if not found
        """
        return get_tile_definition(tile_type)

    def get_terrain_tile_visual_state(
        self, screen: int, tile_x: int, tile_y: int
    ) -> Optional[VisualState]:
        """Get visual state for rendering a terrain tile.

        Args:
            screen: The screen index
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            VisualState if tile has behaviors, None otherwise
        """
        instance = self.terrain_manager.get_instance(screen, tile_x, tile_y)
        if instance is None:
            return None
        return cast(VisualState, instance.state.visual)

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
            if self.is_solid(self.get_terrain_tile(screen, tile_x, bottom_tile)):
                return "ground"

        # Check ceiling collision (top edge)
        for tile_x in range(left_tile, right_tile + 1):
            if self.is_solid(self.get_terrain_tile(screen, tile_x, top_tile)):
                return "ceiling"

        # Check left wall
        for tile_y in range(bottom_tile, top_tile + 1):
            if self.is_solid(self.get_terrain_tile(screen, left_tile, tile_y)):
                return "wall_left"

        # Check right wall
        for tile_y in range(bottom_tile, top_tile + 1):
            if self.is_solid(self.get_terrain_tile(screen, right_tile, tile_y)):
                return "wall_right"

        return None

    def find_zone_position(self, screen: int, zone_char: str) -> Tuple[float, float]:
        """Find center position of a zone.

        Returns the center of a zone in tile coordinates.
        Assumes zone is already validated (1 tile high, contiguous).

        Args:
            screen: Screen index
            zone_char: Zone character to find

        Returns:
            Tuple of (center_x, center_y) in tile coordinates

        Raises:
            ValueError: If zone not found (shouldn't happen after validation)
        """
        if screen not in self.zones:
            raise ValueError(f"Screen {screen} not found in zones")

        zones = self.zones[screen]
        positions = [
            (x, y)
            for y in range(len(zones))
            for x in range(len(zones[0]))
            if zones[y][x] == zone_char
        ]

        if not positions:
            raise ValueError(
                f"Zone '{zone_char}' not found on screen {screen} "
                f"(should have been validated at load time)"
            )

        # Calculate horizontal center (can be fractional)
        x_coords = [x for x, y in positions]
        center_x = (min(x_coords) + max(x_coords)) / 2.0

        # Get y coordinate (all same due to validation)
        center_y = float(positions[0][1])

        return (center_x, center_y)
