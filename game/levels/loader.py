"""YAML level loader for loading level definitions from files."""

import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

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

    name = data.get("name")
    if name is not None:
        if not isinstance(name, str):
            raise ParseError("Level name must be a string if provided")
        level.name = name

    display_name = data.get("display_name")
    if display_name is not None:
        if not isinstance(display_name, str):
            raise ParseError("Level display_name must be a string if provided")
        level.display_name = display_name

    timer_config = data.get("timer")
    if timer_config is not None:
        if not isinstance(timer_config, dict):
            raise ParseError("Level timer must be a mapping if provided")

        timer_start = timer_config.get("start")
        if timer_start is not None:
            try:
                level.timer_start_value = int(timer_start)
            except (TypeError, ValueError) as exc:
                raise ParseError(f"Timer start must be an integer: {exc}") from exc

        frames_per_decrement = timer_config.get("frames_per_decrement")
        if frames_per_decrement is not None:
            try:
                level.timer_frames_per_decrement = int(frames_per_decrement)
            except (TypeError, ValueError) as exc:
                raise ParseError(
                    f"Timer frames_per_decrement must be an integer: {exc}"
                ) from exc

    palette = data.get("palette")
    if palette is not None:
        if not isinstance(palette, str):
            raise ParseError("Level palette must be a string if provided")
        level.default_palette = palette

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
        level.terrain_tiles[screen_idx] = parser.parse_screen(layout, screen_idx)

        # Process background layer if present
        background_layout = screen_data.get("background")
        if background_layout is not None:
            if not isinstance(background_layout, str):
                raise ParseError(f"Screen {screen_idx} background must be a string")

            background_tiles = parser.parse_screen(background_layout, screen_idx)
            terrain_tiles = level.terrain_tiles[screen_idx]
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
                level, screen_idx, screen_data, parser, level.terrain_tiles[screen_idx]
            )

        # Palette override per screen (optional)
        screen_palette = screen_data.get("palette")
        if screen_palette is not None:
            if not isinstance(screen_palette, str):
                raise ParseError(f"Screen {screen_idx} palette must be a string")
            level.set_palette_for_screen(screen_idx, screen_palette)

        # Process spawn data if present
        if "spawn" in screen_data:
            _process_spawn_data(level, screen_idx, screen_data)

    # Snapshot original terrain for resets
    level.snapshot_terrain()

    # Set level dimensions based on parsed screens
    if level.terrain_tiles:
        # Assume all screens have the same dimensions
        first_screen = next(iter(level.terrain_tiles.values()))
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
    from ..terrain.factory import BehaviorFactory

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
                level.register_behavior_spec(screen_idx, x, y, behavior_type, params)
                behavior = factory.create(behavior_type, params if params else None)
                level.terrain_manager.set_tile_behavior(screen_idx, x, y, behavior)
            except Exception as e:
                raise ParseError(
                    f"Screen {screen_idx}: Failed to create behavior "
                    f"for zone '{zone_char}': {e}"
                )


def _process_spawn_data(
    level: Level,
    screen_idx: int,
    screen_data: dict,
) -> None:
    """Process spawn data for a screen.

    Args:
        level: The level being constructed
        screen_idx: Screen index
        screen_data: Screen data from YAML

    Raises:
        ParseError: If validation fails
    """
    from ..spawn import EntitySpec, SpawnTrigger

    spawn_data = screen_data["spawn"]
    if not isinstance(spawn_data, dict):
        raise ParseError(f"Screen {screen_idx} spawn must be a dictionary")

    # Parse the layout if present
    if "layout" not in spawn_data:
        return

    layout_str = spawn_data["layout"]
    if not isinstance(layout_str, str):
        raise ParseError(f"Screen {screen_idx} spawn layout must be a string")

    # Split layout into lines and reverse to get bottom-up order
    lines = layout_str.strip().split("\n")
    lines.reverse()

    if not lines:
        return

    # The bottom row contains trigger symbols
    trigger_row = lines[0]
    # The rest contains spawn location symbols
    location_rows = lines[1:] if len(lines) > 1 else []

    # First pass: collect all entity locations from layout
    entity_locations: Dict[str, List[Tuple[int, int, int]]] = {}
    for tile_y, row in enumerate(location_rows):
        for tile_x, char in enumerate(row):
            if char == ".":
                continue
            if char not in entity_locations:
                entity_locations[char] = []
            entity_locations[char].append((tile_x, tile_y, screen_idx))

    # Parse triggers section if present
    if "triggers" not in spawn_data:
        return

    triggers_data = spawn_data["triggers"]
    if not isinstance(triggers_data, dict):
        raise ParseError(f"Screen {screen_idx} triggers must be a dictionary")

    # Process each trigger
    for trigger_id, trigger_def in triggers_data.items():
        if not isinstance(trigger_def, dict):
            raise ParseError(
                f"Screen {screen_idx}: Trigger '{trigger_id}' must be a dictionary"
            )

        # Find trigger position in the layout
        trigger_tile_x = -1
        for tile_x, char in enumerate(trigger_row):
            if char == trigger_id:
                trigger_tile_x = tile_x
                break

        if trigger_tile_x == -1:
            raise ParseError(
                f"Screen {screen_idx}: Trigger '{trigger_id}' not found in layout"
            )

        # Create trigger
        camera_x = trigger_tile_x * TILE_SIZE
        trigger = SpawnTrigger(
            trigger_id=trigger_id,
            camera_x=camera_x,
            screen=screen_idx,
            tile_x=trigger_tile_x,
        )

        # Process entities for this trigger
        entities_data = trigger_def.get("entities", {})
        if not isinstance(entities_data, dict):
            raise ParseError(
                f"Screen {screen_idx}: Trigger '{trigger_id}' "
                f"entities must be a dictionary"
            )

        for entity_symbol, entity_def in entities_data.items():
            if not isinstance(entity_def, dict):
                raise ParseError(
                    f"Screen {screen_idx}: Entity '{entity_symbol}' "
                    f"must be a dictionary"
                )

            entity_type = entity_def.get("type")
            if not entity_type:
                raise ParseError(
                    f"Screen {screen_idx}: Entity '{entity_symbol}' "
                    f"must have a 'type' field"
                )

            # Get optional parameters
            params = {}
            if "facing" in entity_def:
                params["facing"] = entity_def["facing"]

            # Create entity spec with locations from layout
            entity_spec = EntitySpec(
                entity_type=entity_type,
                params=params,
                symbol=entity_symbol,
                locations=entity_locations.get(entity_symbol, []),
            )

            trigger.entities.append(entity_spec)

        level.spawn_manager.add_trigger(trigger)
