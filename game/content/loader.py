from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping

import yaml

from .sprites import SpriteFrame, SpriteSheetDef
from .tiles import TileDefinition

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

    collision_masks: Mapping[str, int]
    tiles_by_id: Mapping[int, TileDefinition]
    tiles_by_slug: Mapping[str, TileDefinition]


_SPRITE_CACHE: SpriteLibrary | None = None
_TILE_CACHE: TileLibrary | None = None


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

    aggregated: Dict[str, Dict[str, object]] = {}

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
                raise ValueError(f"{path}: sprite sheet '{sheet_name}' must be a mapping")

            # Initialize builder state
            builder = aggregated.setdefault(
                sheet_name, {"image": None, "default_tile_size": None, "sprites": {}}
            )

            image = sheet_payload.get("image")
            if image is not None:
                if not isinstance(image, str):
                    raise ValueError(
                        f"{path}: sprite sheet '{sheet_name}' image must be a string"
                    )
                previous_image = builder["image"]
                if previous_image is None:
                    builder["image"] = image
                elif previous_image != image:
                    raise ValueError(
                        f"{path}: sprite sheet '{sheet_name}' "
                        f"redefines image from {previous_image!r} to {image!r}"
                    )

            default_tile_size = sheet_payload.get("default_tile_size")
            if default_tile_size is not None:
                tile_size_tuple = _coerce_int_pair(
                    default_tile_size, f"{path}: sprite sheet '{sheet_name}' default_tile_size"
                )
                previous_default = builder["default_tile_size"]
                if previous_default is None:
                    builder["default_tile_size"] = tile_size_tuple
                elif previous_default != tile_size_tuple:
                    raise ValueError(
                        f"{path}: sprite sheet '{sheet_name}' "
                        f"redefines default_tile_size from {previous_default} to {tile_size_tuple}"
                    )

            sprites = sheet_payload.get("sprites")
            if not isinstance(sprites, dict):
                raise ValueError(f"{path}: sprite sheet '{sheet_name}' sprites must be a mapping")

            sheet_sprites: Dict[str, SpriteFrame] = builder["sprites"]  # type: ignore[assignment]
            for sprite_name, sprite_data in sprites.items():
                if not isinstance(sprite_name, str):
                    raise ValueError(
                        f"{path}: sprite names in '{sheet_name}' must be strings"
                    )
                if sprite_name in sheet_sprites:
                    raise ValueError(
                        f"{path}: sprite '{sprite_name}' already defined in sheet '{sheet_name}'"
                    )
                if not isinstance(sprite_data, dict):
                    raise ValueError(
                        f"{path}: sprite '{sprite_name}' in sheet '{sheet_name}' must be a mapping"
                    )

                offset = _coerce_int_pair(
                    sprite_data.get("offset"),
                    f"{path}: sprite '{sprite_name}' in sheet '{sheet_name}' offset",
                )
                size = _coerce_int_pair(
                    sprite_data.get("size"),
                    f"{path}: sprite '{sprite_name}' in sheet '{sheet_name}' size",
                )

                sheet_sprites[sprite_name] = SpriteFrame(offset=offset, size=size)

    result: Dict[str, SpriteSheetDef] = {}
    for sheet_name, payload in aggregated.items():
        sprites: Dict[str, SpriteFrame] = payload["sprites"]  # type: ignore[assignment]
        result[sheet_name] = SpriteSheetDef(
            name=sheet_name,
            image=payload["image"],  # type: ignore[arg-type]
            sprites=sprites,
            default_tile_size=payload["default_tile_size"],  # type: ignore[arg-type]
        )

    return result


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

    collision_masks: Dict[str, int] = {}
    tiles_by_id: Dict[int, TileDefinition] = {}
    tiles_by_slug: Dict[str, TileDefinition] = {}

    for path in files:
        with path.open("rb") as fh:
            data = tomllib.load(fh)

        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected table at document root")

        version = data.get("version")
        if version != 1:
            raise ValueError(f"{path}: unsupported version {version!r}")

        mask_table = data.get("collision_masks", {})
        if not isinstance(mask_table, dict):
            raise ValueError(f"{path}: 'collision_masks' must be a table")

        for alias, value in mask_table.items():
            if not isinstance(alias, str):
                raise ValueError(f"{path}: collision mask keys must be strings")
            if alias in collision_masks:
                raise ValueError(
                    f"{path}: collision mask '{alias}' already defined elsewhere"
                )
            if not isinstance(value, int):
                raise ValueError(f"{path}: collision mask '{alias}' must be an integer")
            collision_masks[alias] = value

        tile_entries = data.get("tiles")
        if not isinstance(tile_entries, list):
            raise ValueError(f"{path}: 'tiles' must be an array of tables")

        for entry in tile_entries:
            if not isinstance(entry, dict):
                raise ValueError(f"{path}: tile entries must be tables")

            tile_id = entry.get("id")
            if not isinstance(tile_id, int):
                raise ValueError(f"{path}: tile id must be an integer")
            if tile_id in tiles_by_id:
                raise ValueError(f"{path}: tile id {tile_id} already defined")

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
                    f"{path}: tile '{slug}' references unknown sprite sheet '{sprite_sheet}'"
                )

            sprite = entry.get("sprite")
            if sprite is not None and not isinstance(sprite, str):
                raise ValueError(f"{path}: tile '{slug}' sprite must be null or a string")
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
                raise ValueError(
                    f"{path}: tile '{slug}' collision_mask must be string or integer"
                )

            category = entry.get("category")
            if category is not None and not isinstance(category, str):
                raise ValueError(f"{path}: tile '{slug}' category must be a string if present")

            definition = TileDefinition(
                id=tile_id,
                slug=slug,
                sprite_sheet=sprite_sheet,
                sprite=sprite,
                collision_mask=mask,
                category=category,
            )

            tiles_by_id[tile_id] = definition
            tiles_by_slug[slug] = definition

    return TileLibrary(
        collision_masks=collision_masks,
        tiles_by_id=tiles_by_id,
        tiles_by_slug=tiles_by_slug,
    )


def _coerce_int_pair(value: object, context: str) -> tuple[int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{context} must be a 2-item sequence")

    def _as_int(index: int, raw: object) -> int:
        if not isinstance(raw, int):
            raise ValueError(f"{context}[{index}] must be an integer")
        return raw

    return (_as_int(0, value[0]), _as_int(1, value[1]))
