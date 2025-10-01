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

    return level