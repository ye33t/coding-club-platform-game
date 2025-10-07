"""YAML level loader for loading level definitions from files."""

import logging
from pathlib import Path
from typing import Set

import yaml  # type: ignore[import-untyped]

from ..constants import TILE_SIZE
from ..level import Level
from .parser import LevelParser, ParseError

logger = logging.getLogger(__name__)


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

        # Process background layer if present
        background_layout = screen_data.get("background")
        if background_layout is not None:
            if not isinstance(background_layout, str):
                raise ParseError(f"Screen {screen_idx} background must be a string")

            background_tiles = parser.parse_screen(background_layout, screen_idx)
            terrain_tiles = level.tiles[screen_idx]
            if len(background_tiles) != len(terrain_tiles):
                raise ParseError(
                    f"Screen {screen_idx} background must match layout height"
                )
            if terrain_tiles and background_tiles:
                if len(background_tiles[0]) != len(terrain_tiles[0]):
                    raise ParseError(
                        f"Screen {screen_idx} background must match layout width"
                    )

            level.background_tiles[screen_idx] = background_tiles

        # Process zones and behaviors if present
        has_zones = "zones" in screen_data
        has_behaviors = "behaviors" in screen_data

        # Validate that zones and behaviors are both present or both absent
        if has_zones and not has_behaviors:
            raise ParseError(
                f"Screen {screen_idx} has 'zones' but no 'behaviors' section"
            )
        if has_behaviors and not has_zones:
            raise ParseError(
                f"Screen {screen_idx} has 'behaviors' but no 'zones' section"
            )

        if has_zones and has_behaviors:
            _process_zones_and_behaviors(
                level, screen_idx, screen_data, parser, level.tiles[screen_idx]
            )

    # Set level dimensions based on parsed screens
    if level.tiles:
        # Assume all screens have the same dimensions
        first_screen = next(iter(level.tiles.values()))
        level.height_tiles = len(first_screen)
        level.width_tiles = len(first_screen[0]) if first_screen else 0
        level.width_pixels = level.width_tiles * TILE_SIZE
        level.height_pixels = level.height_tiles * TILE_SIZE

    # Validate all behaviors with complete level context
    for instance in level.terrain_manager.instances.values():
        if instance.behavior:
            try:
                instance.behavior.validate(level)
            except ValueError as e:
                raise ParseError(
                    f"Behavior validation failed at screen {instance.screen}, "
                    f"tile ({instance.x}, {instance.y}): {e}"
                )

    return level


def _process_zones_and_behaviors(
    level: Level,
    screen_idx: int,
    screen_data: dict,
    parser: LevelParser,
    tiles: list,
) -> None:
    """Process zones and behaviors for a screen.

    Args:
        level: The level being constructed
        screen_idx: Screen index
        screen_data: Screen data from YAML
        parser: The level parser
        tiles: Parsed tiles for this screen

    Raises:
        ParseError: If validation fails
    """
    zones_str = screen_data["zones"]
    behaviors_dict = screen_data["behaviors"]

    if not isinstance(zones_str, str):
        raise ParseError(f"Screen {screen_idx} zones must be a string")

    if not isinstance(behaviors_dict, dict):
        raise ParseError(f"Screen {screen_idx} behaviors must be a dictionary")

    # Parse zones grid
    height = len(tiles)
    width = len(tiles[0]) if tiles else 0
    zones = parser.parse_zones(zones_str, width, height)

    # Store zones in level
    level.zones[screen_idx] = zones

    # Collect all zone characters used in the grid (excluding '.')
    used_zones: Set[str] = set()
    for row in zones:
        for char in row:
            if char != ".":
                used_zones.add(char)

    # Validate that all used zones are defined in behaviors
    undefined_zones = used_zones - behaviors_dict.keys()
    if undefined_zones:
        zones_list = ", ".join(f"'{z}'" for z in sorted(undefined_zones))
        raise ParseError(
            f"Screen {screen_idx}: Zone(s) {zones_list} used in grid "
            f"but not defined in behaviors section"
        )

    # Warn about unused behaviors
    unused_behaviors = behaviors_dict.keys() - used_zones
    if unused_behaviors:
        zones_list = ", ".join(f"'{z}'" for z in sorted(unused_behaviors))
        logger.warning(
            f"Screen {screen_idx}: Behavior(s) {zones_list} defined "
            f"but not used in zones grid"
        )

    # Create behavior factory (import here to avoid circular imports)
    from ..terrain import BehaviorFactory

    factory = BehaviorFactory()

    # Process each zone and assign behaviors
    for y in range(height):
        for x in range(width):
            zone_char = zones[y][x]
            if zone_char == ".":
                continue

            # Get behavior config
            behavior_config = behaviors_dict[zone_char]
            if not isinstance(behavior_config, dict):
                raise ParseError(
                    f"Screen {screen_idx}: Behavior for zone '{zone_char}' "
                    f"must be a dictionary"
                )

            if "type" not in behavior_config:
                raise ParseError(
                    f"Screen {screen_idx}: Behavior for zone '{zone_char}' "
                    f"must have a 'type' field"
                )

            behavior_type = behavior_config["type"]
            if not isinstance(behavior_type, str):
                raise ParseError(
                    f"Screen {screen_idx}: Behavior type for zone '{zone_char}' "
                    f"must be a string"
                )

            # Extract parameters (everything except "type")
            params = {k: v for k, v in behavior_config.items() if k != "type"}

            # Create behavior instance and assign to tile
            try:
                behavior = factory.create(behavior_type, params if params else None)
                level.terrain_manager.set_tile_behavior(screen_idx, x, y, behavior)
            except Exception as e:
                raise ParseError(
                    f"Screen {screen_idx}: Failed to create behavior "
                    f"for zone '{zone_char}': {e}"
                )
