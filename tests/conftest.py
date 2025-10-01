"""Shared test fixtures using real objects."""

import pytest

from game.camera import Camera, CameraState
from game.constants import TILE_SIZE
from game.level import Level
from game.tile_definitions import TILE_EMPTY, TILE_GROUND
from game.mario import MarioIntent, MarioState
from game.physics import PhysicsContext


@pytest.fixture
def empty_level():
    """Create a real empty level for testing."""
    level = Level()
    # Set spawn point
    level.spawn_tile_x = 3
    level.spawn_tile_y = 7
    level.spawn_screen = 0
    # Set dimensions (2 screens wide, standard height)
    level.width_tiles = 32  # 2 screens * 16 tiles per screen
    level.height_tiles = 14
    level.width_pixels = level.width_tiles * TILE_SIZE
    level.height_pixels = level.height_tiles * TILE_SIZE
    # Clear the entire level for screen 0
    level.tiles[0] = []
    for y in range(level.height_tiles):
        row = [TILE_EMPTY] * level.width_tiles
        level.tiles[0].append(row)
    return level


@pytest.fixture
def level_with_ground():
    """Create a level with just ground at bottom."""
    level = Level()
    # Set spawn point
    level.spawn_tile_x = 3
    level.spawn_tile_y = 7
    level.spawn_screen = 0
    # Set dimensions (2 screens wide, standard height)
    level.width_tiles = 32  # 2 screens * 16 tiles per screen
    level.height_tiles = 14
    level.width_pixels = level.width_tiles * TILE_SIZE
    level.height_pixels = level.height_tiles * TILE_SIZE
    # Clear the level first for screen 0
    level.tiles[0] = []
    for y in range(level.height_tiles):
        row = [TILE_EMPTY] * level.width_tiles
        level.tiles[0].append(row)
    # Add ground at the bottom
    for x in range(level.width_tiles):
        level.tiles[0][0][x] = TILE_GROUND
        level.tiles[0][1][x] = TILE_GROUND
    return level


@pytest.fixture
def level_with_platform():
    """Create a level with ground and a platform."""
    level = Level()
    # Set spawn point
    level.spawn_tile_x = 3
    level.spawn_tile_y = 7
    level.spawn_screen = 0
    # Set dimensions (2 screens wide, standard height)
    level.width_tiles = 32  # 2 screens * 16 tiles per screen
    level.height_tiles = 14
    level.width_pixels = level.width_tiles * TILE_SIZE
    level.height_pixels = level.height_tiles * TILE_SIZE
    # Clear the level first for screen 0
    level.tiles[0] = []
    for y in range(level.height_tiles):
        row = [TILE_EMPTY] * level.width_tiles
        level.tiles[0].append(row)
    # Add ground at the bottom
    for x in range(level.width_tiles):
        level.tiles[0][0][x] = TILE_GROUND
        level.tiles[0][1][x] = TILE_GROUND
    # Add a platform at height 5
    for x in range(10, 15):
        level.tiles[0][5][x] = TILE_GROUND
    return level




@pytest.fixture
def camera():
    """Create a real camera at origin."""
    return Camera()


@pytest.fixture
def camera_state():
    """Create a camera state at origin."""
    return CameraState()


@pytest.fixture
def mario_state():
    """Create a basic Mario state."""
    return MarioState(x=100.0, y=50.0, vx=0.0, vy=0.0)


@pytest.fixture
def mario_intent():
    """Create an empty Mario intent."""
    return MarioIntent()


@pytest.fixture
def basic_context(empty_level, camera_state, mario_state, mario_intent):
    """Create a basic physics context with real objects."""
    return PhysicsContext(
        mario_state=mario_state,
        mario_intent=mario_intent,
        dt=1 / 60,  # Standard 60 FPS frame time
        level=empty_level,
        camera_state=camera_state,
    )
