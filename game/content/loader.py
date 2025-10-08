from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping

import yaml  # type: ignore[import]

from .types import SpriteFrame, SpriteSheetDef, TileConfig

ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
SPRITE_DEFINITION_DIR = ASSET_ROOT / "sprites"
TILE_DEFINITION_DIR = ASSET_ROOT / "tiles"


@dataclass(frozen=True, slots=True)
class SpriteLibrary:
    """Container for all sprite sheet definitions."""

    sheets: Mapping[str, SpriteSheetDef]


@dataclass(frozen=True, slots=True)
class TileLibrary:
    """Container for all tile definitions."""

    tiles: Mapping[str, TileConfig]
    simple_tiles: Mapping[str, str]


_SPRITE_CACHE: SpriteLibrary | None = None
_TILE_CACHE: TileLibrary | None = None


@dataclass(slots=True)
class _SpriteSheetBuilder:
    image: str | None = None
    default_tile_size: tuple[int, int] | None = None
    colorkey: tuple[int, int, int] | str | None = None
    sprites: Dict[str, SpriteFrame] = field(default_factory=dict)


def load_sprite_sheets(reload: bool = False) -> SpriteLibrary:
    """Load sprite sheet metadata from YAML files."""

    global _SPRITE_CACHE

    if not reload and _SPRITE_CACHE is not None:
        return _SPRITE_CACHE

    sheets = _parse_sprite_definitions()
    _SPRITE_CACHE = SpriteLibrary(sheets=sheets)
    return _SPRITE_CACHE


def load_tiles(reload: bool = False) -> TileLibrary:
    """Load tile metadata from TOML files."""

    global _TILE_CACHE

    if not reload and _TILE_CACHE is not None:
        return _TILE_CACHE

    sprite_library = load_sprite_sheets(reload=reload)
    tile_library = _parse_tile_definitions(sprite_library)
    _TILE_CACHE = tile_library
    return tile_library


def _parse_sprite_definitions() -> Dict[str, SpriteSheetDef]:
    if not SPRITE_DEFINITION_DIR.exists():
        raise FileNotFoundError(
            f"Missing sprite definition directory: {SPRITE_DEFINITION_DIR}"
        )

    aggregated: Dict[str, _SpriteSheetBuilder] = {}

    files = sorted(SPRITE_DEFINITION_DIR.glob("*.yaml"))
    if not files:
        raise FileNotFoundError(
            f"No sprite definition files found in {SPRITE_DEFINITION_DIR}"
        )

    for path in files:
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected mapping at document root")

        version = data.get("version")
        if version != 1:
            raise ValueError(f"{path}: unsupported version {version!r}")

        definitions = data.get("sprite_sheets")
        if not isinstance(definitions, dict):
            raise ValueError(f"{path}: 'sprite_sheets' must be a mapping")

        for sheet_name, sheet_payload in definitions.items():
            if not isinstance(sheet_name, str):
                raise ValueError(f"{path}: sprite sheet keys must be strings")
            if not isinstance(sheet_payload, dict):
                raise ValueError(
                    f"{path}: sprite sheet '{sheet_name}' must be a mapping"
                )

            builder = aggregated.setdefault(sheet_name, _SpriteSheetBuilder())

            image = sheet_payload.get("image")
            if image is not None:
                if not isinstance(image, str):
                    raise ValueError(
                        f"{path}: sprite sheet '{sheet_name}' image must be a string"
                    )
                previous_image = builder.image
                if previous_image is None:
                    builder.image = image
                elif previous_image != image:
                    raise ValueError(
                        f"{path}: sprite sheet '{sheet_name}' "
                        f"redefines image from {previous_image!r} to {image!r}"
                    )

            default_tile_size = sheet_payload.get("default_tile_size")
            if default_tile_size is not None:
                tile_size_tuple = _coerce_int_pair(
                    default_tile_size,
                    f"{path}: sprite sheet '{sheet_name}' default_tile_size",
                )
                previous_default = builder.default_tile_size
                if previous_default is None:
                    builder.default_tile_size = tile_size_tuple
                elif previous_default != tile_size_tuple:
                    raise ValueError(
                        f"{path}: sprite sheet '{sheet_name}' "
                        f"redefines default_tile_size from {previous_default} "
                        f"to {tile_size_tuple}"
                    )

            colorkey_value = sheet_payload.get("colorkey")
            if colorkey_value is not None:
                coerced_colorkey = _coerce_colorkey(
                    colorkey_value,
                    f"{path}: sprite sheet '{sheet_name}' colorkey",
                )
                previous_colorkey = builder.colorkey
                if previous_colorkey is None:
                    builder.colorkey = coerced_colorkey
                elif previous_colorkey != coerced_colorkey:
                    raise ValueError(
                        f"{path}: sprite sheet '{sheet_name}' "
                        f"redefines colorkey from {previous_colorkey} "
                        f"to {coerced_colorkey}"
                    )

            sprites = sheet_payload.get("sprites")
            if not isinstance(sprites, dict):
                raise ValueError(
                    f"{path}: sprite sheet '{sheet_name}' sprites must be a mapping"
                )

            for sprite_name, sprite_data in sprites.items():
                if not isinstance(sprite_name, str):
                    raise ValueError(
                        f"{path}: sprite names in '{sheet_name}' must be strings"
                    )
                if sprite_name in builder.sprites:
                    raise ValueError(
                        f"{path}: sprite '{sprite_name}' already defined "
                        f"in sheet '{sheet_name}'"
                    )
                if not isinstance(sprite_data, dict):
                    raise ValueError(
                        f"{path}: sprite '{sprite_name}' in sheet "
                        f"'{sheet_name}' must be a mapping"
                    )

                offset = _coerce_int_pair(
                    sprite_data.get("offset"),
                    f"{path}: sprite '{sprite_name}' in sheet '{sheet_name}' offset",
                )
                size = _coerce_int_pair(
                    sprite_data.get("size"),
                    f"{path}: sprite '{sprite_name}' in sheet '{sheet_name}' size",
                )

                builder.sprites[sprite_name] = SpriteFrame(offset=offset, size=size)

    return {
        sheet_name: SpriteSheetDef(
            name=sheet_name,
            image=builder.image,
            sprites=builder.sprites,
            default_tile_size=builder.default_tile_size,
            colorkey=builder.colorkey,
        )
        for sheet_name, builder in aggregated.items()
    }


def _parse_tile_definitions(sprite_library: SpriteLibrary) -> TileLibrary:
    if not TILE_DEFINITION_DIR.exists():
        raise FileNotFoundError(
            f"Missing tile definition directory: {TILE_DEFINITION_DIR}"
        )

    files = sorted(TILE_DEFINITION_DIR.glob("*.toml"))
    if not files:
        raise FileNotFoundError(
            f"No tile definition files found in {TILE_DEFINITION_DIR}"
        )

    tiles_by_slug: Dict[str, TileConfig] = {}
    simple_tiles: Dict[str, str] = {}

    for path in files:
        with path.open("rb") as fh:
            data = tomllib.load(fh)

        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected table at document root")

        version = data.get("version")
        if version != 1:
            raise ValueError(f"{path}: unsupported version {version!r}")

        mask_table = data.get("collision_masks", {})
        collision_masks: Dict[str, int] = {}
        if isinstance(mask_table, dict):
            for alias, value in mask_table.items():
                if not isinstance(alias, str):
                    raise ValueError(f"{path}: collision mask keys must be strings")
                if alias in collision_masks:
                    raise ValueError(
                        f"{path}: collision mask '{alias}' already defined elsewhere"
                    )
                if not isinstance(value, int):
                    raise ValueError(
                        f"{path}: collision mask '{alias}' must be an integer"
                    )
                collision_masks[alias] = value
        else:
            raise ValueError(f"{path}: 'collision_masks' must be a mapping")

        tile_entries = data.get("tiles")
        if not isinstance(tile_entries, list):
            raise ValueError(f"{path}: 'tiles' must be an array of tables")

        for entry in tile_entries:
            if not isinstance(entry, dict):
                raise ValueError(f"{path}: tile entries must be tables")

            slug = entry.get("slug")
            if not isinstance(slug, str):
                raise ValueError(f"{path}: tile slug must be a string")
            if slug in tiles_by_slug:
                raise ValueError(f"{path}: tile slug '{slug}' already defined")

            sprite_sheet = entry.get("sprite_sheet")
            if not isinstance(sprite_sheet, str):
                raise ValueError(f"{path}: tile '{slug}' sprite_sheet must be a string")
            if sprite_sheet not in sprite_library.sheets:
                raise ValueError(
                    f"{path}: tile '{slug}' references unknown sprite sheet "
                    f"'{sprite_sheet}'"
                )

            sprite = entry.get("sprite")
            if sprite is not None and not isinstance(sprite, str):
                raise ValueError(
                    f"{path}: tile '{slug}' sprite must be null or a string"
                )
            if sprite is not None:
                sheet = sprite_library.sheets[sprite_sheet]
                if sprite not in sheet.sprites:
                    raise ValueError(
                        f"{path}: tile '{slug}' references unknown sprite '{sprite}' "
                        f"in sheet '{sprite_sheet}'"
                    )

            collision_mask_value = entry.get("collision_mask")
            if isinstance(collision_mask_value, str):
                if collision_mask_value not in collision_masks:
                    raise ValueError(
                        f"{path}: tile '{slug}' references unknown collision mask "
                        f"'{collision_mask_value}'"
                    )
                mask = collision_masks[collision_mask_value]
            elif isinstance(collision_mask_value, int):
                mask = collision_mask_value
            else:
                mask = 0

            category = entry.get("category")
            if category is not None and not isinstance(category, str):
                raise ValueError(
                    f"{path}: tile '{slug}' category must be a string if present"
                )

            simple_key = entry.get("simple_key")
            if simple_key is not None:
                if not isinstance(simple_key, str):
                    raise ValueError(
                        f"{path}: tile '{slug}' simple_key must be a string if provided"
                    )
                if len(simple_key) != 1:
                    raise ValueError(
                        f"{path}: tile '{slug}' simple_key must be a single character"
                    )
                if simple_key in simple_tiles:
                    raise ValueError(
                        f"{path}: simple_key '{simple_key}' already assigned to tile "
                        f"'{simple_tiles[simple_key]}'"
                    )

            definition = TileConfig(
                slug=slug,
                sprite_sheet=sprite_sheet,
                sprite=sprite,
                collision_mask=mask,
                category=category,
                simple_key=simple_key,
            )

            tiles_by_slug[slug] = definition
            if simple_key is not None:
                simple_tiles[simple_key] = slug

    return TileLibrary(
        tiles=tiles_by_slug,
        simple_tiles=simple_tiles,
    )


def _coerce_int_pair(value: object, context: str) -> tuple[int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{context} must be a 2-item sequence")

    def _as_int(index: int, raw: object) -> int:
        if not isinstance(raw, int):
            raise ValueError(f"{context}[{index}] must be an integer")
        return raw

    return (_as_int(0, value[0]), _as_int(1, value[1]))


def _coerce_colorkey(value: object, context: str) -> tuple[int, int, int] | str:
    if isinstance(value, str):
        if value != "auto":
            raise ValueError(f"{context} string value must be 'auto'")
        return value
    if isinstance(value, (list, tuple)) and len(value) == 3:
        components: list[int] = []
        for idx, raw in enumerate(value):
            if not isinstance(raw, int):
                raise ValueError(f"{context}[{idx}] must be an integer")
            if not 0 <= raw <= 255:
                raise ValueError(f"{context}[{idx}] must be between 0 and 255")
            components.append(raw)
        return tuple(components)  # type: ignore[return-value]
    raise ValueError(f"{context} must be 'auto' or a 3-item sequence of integers")
