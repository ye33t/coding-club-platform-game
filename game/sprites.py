"""Global sprite manager for all sprite sheets."""

from __future__ import annotations

import os
from typing import Dict, Iterable

import pygame
from pygame import Surface

from .constants import TRANSPARENT
from .content import SpriteLibrary, load_sprite_sheets
from .content.sprites import SpriteSheetDef
from .sprite_sheet import SpriteSheet


class SpriteManager:
    """Manages all sprite sheets and provides global sprite access."""

    _instance = None

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the sprite manager."""
        if getattr(self, "_initialized", False):
            return

        self.sheets: Dict[str, SpriteSheet] = {}
        self.sprites: Dict[str, Dict[str, Surface]] = {}
        self.sheet_defs: Dict[str, SpriteSheetDef] = {}
        self._initialized = True

    def load_sheets(self, assets_path: str):
        """Load all sprite sheets.

        Args:
            assets_path: Path to the directory containing sprite sheet images.
        """

        library: SpriteLibrary = load_sprite_sheets()
        self.sheet_defs = dict(library.sheets)

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

    def draw_at_position(
        self,
        surface: Surface,
        sheet_name: str,
        sprite_name: str,
        x: int,
        y: int,
        reflected: bool = False,
    ):
        """Draw a sprite at pixel coordinates with bottom-left alignment."""

        sprite = self.get(sheet_name, sprite_name)
        if sprite is None:
            return

        # Lazy import to avoid circular dependency during initialization
        from .constants import NATIVE_HEIGHT

        if reflected:
            sprite = pygame.transform.flip(sprite, True, False)

        screen_y = NATIVE_HEIGHT - y
        draw_y = screen_y - sprite.get_height()

        surface.blit(sprite, (x, draw_y))

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


# Global sprite manager instance
sprites = SpriteManager()
