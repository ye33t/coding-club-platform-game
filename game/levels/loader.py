"""YAML level loader for loading level definitions from files."""

from pathlib import Path

import yaml

from .parser import LevelParser, ParseError
from ..level import Level


def load(filepath: str) -> Level:
    """Load a level from a YAML file.

    Args:
        filepath: Path to the YAML file

    Returns:
        Level instance populated with tile data

    Raises:
        FileNotFoundError: If the file doesn't exist
        ParseError: If parsing fails
        yaml.YAMLError: If YAML is invalid
    """
    # Create empty level to populate
    level = Level()

    # Create parser for this operation
    parser = LevelParser()

    # Load the file directly - no fallbacks
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Level file not found: {filepath}")

    # Load YAML
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Validate structure
    if not isinstance(data, dict):
        raise ParseError("Level file must contain a YAML dictionary")

    if "screens" not in data:
        raise ParseError("Level file must have a 'screens' section")

    if "spawn" not in data:
        raise ParseError("Level file must have a 'spawn' section")

    # Parse spawn point
    spawn = data["spawn"]
    if not isinstance(spawn, dict):
        raise ParseError("Spawn must be a dictionary with tile_x, tile_y, and screen")

    if "tile_x" not in spawn:
        raise ParseError("Spawn must have a 'tile_x' field")
    if "tile_y" not in spawn:
        raise ParseError("Spawn must have a 'tile_y' field")
    if "screen" not in spawn:
        raise ParseError("Spawn must have a 'screen' field")

    try:
        level.spawn_tile_x = int(spawn["tile_x"])
        level.spawn_tile_y = int(spawn["tile_y"])
        level.spawn_screen = int(spawn["screen"])
    except (ValueError, TypeError) as e:
        raise ParseError(f"Spawn coordinates must be integers: {e}")

    # Parse screens and populate level
    for screen_idx, screen_data in data["screens"].items():
        # Convert screen index to int
        try:
            screen_idx = int(screen_idx)
        except (ValueError, TypeError):
            raise ParseError(f"Screen index must be an integer, got {screen_idx}")

        # Get layout
        if not isinstance(screen_data, dict) or "layout" not in screen_data:
            raise ParseError(f"Screen {screen_idx} must have a 'layout' field")

        layout = screen_data["layout"]
        if not isinstance(layout, str):
            raise ParseError(f"Screen {screen_idx} layout must be a string")

        # Parse the layout and add to level
        level.tiles[screen_idx] = parser.parse_screen(layout, screen_idx)

    # Set level dimensions based on parsed screens
    if level.tiles:
        # Assume all screens have the same dimensions
        first_screen = next(iter(level.tiles.values()))
        level.height_tiles = len(first_screen)
        level.width_tiles = len(first_screen[0]) if first_screen else 0
        level.width_pixels = level.width_tiles * 16  # BLOCK_SIZE = 16
        level.height_pixels = level.height_tiles * 16

    return level