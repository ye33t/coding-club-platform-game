"""Global sprite manager for all sprite sheets."""

from __future__ import annotations

import math
import os
from typing import Dict, Iterable, Mapping, Optional, Tuple

import pygame
from pygame import Surface

from ..constants import TRANSPARENT
from .loader import SpriteLibrary, load_sprite_sheets
from .sprite_sheet import SpriteSheet
from .types import SpriteSheetDef


class SpriteManager:
    """Manages all sprite sheets and provides global sprite access."""

    _instance = None

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the sprite manager."""
        if getattr(self, "_initialized", False):
            return

        self.sheets: Dict[str, SpriteSheet] = {}
        self.sprites: Dict[str, Dict[str, Surface]] = {}
        self.sheet_defs: Dict[str, SpriteSheetDef] = {}
        self.palette_cache: Dict[Tuple[int, str], Dict[str, Dict[str, Surface]]] = {}
        self._palette_cache_version: Optional[int] = None
        self._initialized = True

    def load_sheets(self, assets_path: str):
        """Load all sprite sheets.

        Args:
            assets_path: Path to the directory containing sprite sheet images.
        """

        library: SpriteLibrary = load_sprite_sheets()
        self.sheet_defs = dict(library.sheets)
        self.palette_cache.clear()
        self._palette_cache_version = None

        for sheet_name, sheet_def in self.sheet_defs.items():
            filename = sheet_def.image or f"{sheet_name}.png"
            colorkey = sheet_def.colorkey or TRANSPARENT
            filepath = os.path.join(assets_path, filename)

            if os.path.exists(filepath):
                self.sheets[sheet_name] = SpriteSheet(filepath, colorkey)
                self.sprites[sheet_name] = {}
                print(f"Loaded sprite sheet: {sheet_name}")
            else:
                print(f"Warning: Could not find sprite sheet image {filename}")

    def get(self, sheet_name: str, sprite_name: str) -> Surface | None:
        """Get a sprite by sheet and sprite name."""

        # Use cached surface if available
        cached_sheet = self.sprites.get(sheet_name)
        if cached_sheet and sprite_name in cached_sheet:
            return cached_sheet[sprite_name]

        sprite_sheet = self.sheets.get(sheet_name)
        if sprite_sheet is None:
            print(f"Warning: Sheet '{sheet_name}' not loaded")
            return None

        sheet_def = self.sheet_defs.get(sheet_name)
        if sheet_def is None:
            print(f"Warning: No definitions loaded for sheet '{sheet_name}'")
            return None

        sprite_def = sheet_def.sprites.get(sprite_name)
        if sprite_def is None:
            print(
                f"Warning: Sprite '{sprite_name}' not defined in sheet '{sheet_name}'"
            )
            return None

        x, y = sprite_def.offset
        tile_width, tile_height = sprite_def.size
        surface = sprite_sheet.get_sprite(x, y, tile_width, tile_height)

        cached_sheet = self.sprites.setdefault(sheet_name, {})
        cached_sheet[sprite_name] = surface
        return surface

    def get_with_palette(
        self,
        sheet_name: str,
        sprite_name: str,
        scheme_name: str | None = None,
    ) -> Surface | None:
        """Get a sprite surface remapped for the requested palette scheme."""

        from .palettes import palettes

        base_surface = self.get(sheet_name, sprite_name)
        if base_surface is None:
            return None

        # Resolve palette mapping
        version = palettes.version
        if self._palette_cache_version != version:
            self.palette_cache.clear()
            self._palette_cache_version = version

        active_scheme = scheme_name or palettes.active_scheme_name
        scheme = palettes.get_scheme(active_scheme)
        color_map = palettes.color_map_for(scheme.name, sheet_name)
        if not color_map:
            return base_surface

        cache_key = (version, scheme.name)
        scheme_cache = self.palette_cache.setdefault(cache_key, {})
        sheet_cache = scheme_cache.setdefault(sheet_name, {})
        cached_surface = sheet_cache.get(sprite_name)
        if cached_surface is not None:
            return cached_surface

        tinted = self._apply_palette(base_surface, color_map)
        sheet_cache[sprite_name] = tinted
        return tinted

    def draw_at_position(
        self,
        surface: Surface,
        sheet_name: str,
        sprite_name: str,
        x: float,
        y: float,
        reflected: bool = False,
        palette: str | None = None,
        *,
        rotation_degrees: float = 0.0,
        anchor: str = "bottomleft",
    ):
        """Draw a sprite at pixel coordinates with bottom-left alignment."""

        sprite = self.get_with_palette(sheet_name, sprite_name, palette)
        if sprite is None:
            if sprite_name != "empty":
                raise ValueError(f"Sprite not found: {sheet_name}/{sprite_name}")
            return

        # Lazy import to avoid circular dependency during initialization
        from ..constants import NATIVE_HEIGHT

        if reflected:
            sprite = pygame.transform.flip(sprite, True, False)

        width, height = sprite.get_size()

        anchor_key = anchor.lower()
        if anchor_key not in {"bottomleft", "center"}:
            raise ValueError(
                f"Unsupported anchor '{anchor}'. Expected 'bottomleft' or 'center'."
            )

        rotation_normalized = rotation_degrees % 360.0
        if math.isclose(rotation_normalized, 0.0, abs_tol=1e-6):
            rotation_normalized = 0.0

        if rotation_normalized == 0.0:
            if anchor_key == "bottomleft":
                screen_bottom = NATIVE_HEIGHT - y
                draw_x = int(round(x))
                draw_y = int(round(screen_bottom - height))
            else:  # center
                screen_center_y = NATIVE_HEIGHT - y
                draw_x = int(round(x - width / 2))
                draw_y = int(round(screen_center_y - height / 2))
            surface.blit(sprite, (draw_x, draw_y))
            return

        pivot_local: pygame.math.Vector2
        if anchor_key == "bottomleft":
            pivot_local = pygame.math.Vector2(0.0, float(height))
        else:  # center
            pivot_local = pygame.math.Vector2(width / 2, height / 2)

        sprite_center = pygame.math.Vector2(width / 2, height / 2)
        offset_to_pivot = pivot_local - sprite_center
        rotated_offset = offset_to_pivot.rotate(rotation_normalized)

        rotated = pygame.transform.rotate(sprite, rotation_normalized)
        pivot_screen = pygame.math.Vector2(float(x), float(NATIVE_HEIGHT - y))
        rotated_center = pivot_screen - rotated_offset

        rotated_rect = rotated.get_rect()
        rotated_rect.center = (
            int(round(rotated_center.x)),
            int(round(rotated_center.y)),
        )

        surface.blit(rotated, rotated_rect.topleft)

    def preload_sprites(
        self, sheet_name: str, sprite_names: Iterable[str] | None = None
    ):
        """Preload sprites into cache for faster access."""

        sheet_def = self.sheet_defs.get(sheet_name)
        if sheet_def is None:
            return

        if sprite_names is None:
            sprites_to_load = list(sheet_def.sprites.keys())
        else:
            sprites_to_load = list(sprite_names)

        for sprite_name in sprites_to_load:
            self.get(sheet_name, sprite_name)

        print(f"Preloaded {len(sprites_to_load)} sprites from {sheet_name}")

    @staticmethod
    def _apply_palette(
        base_surface: Surface,
        color_map: Mapping[tuple[int, int, int], tuple[int, int, int]],
    ) -> Surface:
        """Return a tinted copy of the base surface by applying color remaps."""

        tinted = base_surface.copy()
        try:
            pixel_array = pygame.PixelArray(tinted)
        except pygame.error:
            width, height = tinted.get_size()
            tinted.lock()
            try:
                for x in range(width):
                    for y in range(height):
                        color = tinted.get_at((x, y))
                        rgb = (color.r, color.g, color.b)
                        target = color_map.get(rgb)
                        if target is None:
                            continue
                        tinted.set_at((x, y), (*target, color.a))
            finally:
                tinted.unlock()
        else:
            try:
                for base_color, target_color in color_map.items():
                    if base_color == target_color:
                        continue
                    old_value = tinted.map_rgb(base_color)
                    new_value = tinted.map_rgb(target_color)
                    pixel_array.replace(old_value, new_value)
            finally:
                del pixel_array

        return tinted


# Global sprite manager instance
sprites = SpriteManager()
