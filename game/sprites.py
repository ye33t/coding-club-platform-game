"""Global sprite manager for all sprite sheets."""

import os
import pygame
from .sprite_sheet import SpriteSheet
from .sprite_definitions import SPRITE_SHEETS
from .constants import TILE_SIZE, tiles_to_pixels, TRANSPARENT


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
        if self._initialized:
            return

        self.sheets = {}
        self.sprites = {}
        self._initialized = True

    def load_sheets(self, assets_path):
        """Load all sprite sheets.

        Args:
            assets_path: Path to the assets directory
        """
        # Define sheet files and their transparency colors
        sheet_configs = {
            "characters": ("characters.png", TRANSPARENT),
            "blocks": ("blocks.png", "auto"),
            "enemies": ("enemies.png", TRANSPARENT),
            "background": ("background.png", TRANSPARENT),
            "other": ("other.png", TRANSPARENT),
        }

        for sheet_name, (filename, colorkey) in sheet_configs.items():
            filepath = os.path.join(assets_path, filename)

            if os.path.exists(filepath):
                self.sheets[sheet_name] = SpriteSheet(filepath, colorkey)
                self.sprites[sheet_name] = {}
                print(f"Loaded sprite sheet: {sheet_name}")
            else:
                print(f"Warning: Could not find sprite sheet {filename}")

    def get(self, sheet_name, sprite_name):
        """Get a sprite by sheet and sprite name.

        Args:
            sheet_name: Name of the sprite sheet (e.g., "characters")
            sprite_name: Name of the sprite (e.g., "small_mario_stand")

        Returns:
            pygame.Surface containing the sprite, or None if not found
        """
        # Check if sprite is already cached
        if sheet_name in self.sprites and sprite_name in self.sprites[sheet_name]:
            return self.sprites[sheet_name][sprite_name]

        # Check if sheet exists
        if sheet_name not in self.sheets:
            print(f"Warning: Sheet '{sheet_name}' not loaded")
            return None

        # Check if sprite definition exists
        if sheet_name not in SPRITE_SHEETS or sprite_name not in SPRITE_SHEETS[sheet_name]:
            print(f"Warning: Sprite '{sprite_name}' not defined in sheet '{sheet_name}'")
            return None

        # Extract sprite using definition
        # Format: (x, y, tile_width, tile_height)
        sprite_def = SPRITE_SHEETS[sheet_name][sprite_name]
        if len(sprite_def) == 4:
            x, y, tile_width, tile_height = sprite_def
            # Extract sprite using bottom-left coordinates
            sprite = self.sheets[sheet_name].get_sprite(x, y, tile_width, tile_height)
        else:
            print(f"Warning: Invalid sprite definition format for {sprite_name}")
            return None

        # Cache the sprite
        self.sprites[sheet_name][sprite_name] = sprite

        return sprite

    def get_info(self, sheet_name, sprite_name):
        """Get sprite info including tile dimensions.

        Args:
            sheet_name: Name of the sprite sheet
            sprite_name: Name of the sprite

        Returns:
            Dict with sprite info or None if not found
        """
        if sheet_name not in SPRITE_SHEETS or sprite_name not in SPRITE_SHEETS[sheet_name]:
            return None

        sprite_def = SPRITE_SHEETS[sheet_name][sprite_name]
        if len(sprite_def) == 4:
            x, y, tile_width, tile_height = sprite_def
            return {
                "tile_width": tile_width,
                "tile_height": tile_height,
                "pixel_width": tile_width * TILE_SIZE,
                "pixel_height": tile_height * TILE_SIZE,
            }
        return None

    def draw_at_tile(self, surface, sheet_name, sprite_name, tile_x, tile_y):
        """Draw a sprite at tile coordinates with bottom-left alignment.

        Uses bottom-up coordinate system where y=0 is at the bottom of the screen.

        Args:
            surface: Surface to draw on
            sheet_name: Name of the sprite sheet
            sprite_name: Name of the sprite
            tile_x: X position in tiles (left edge)
            tile_y: Y position in tiles from bottom (bottom edge of sprite)
        """
        sprite = self.get(sheet_name, sprite_name)
        if not sprite:
            return

        # Get screen height in tiles
        from .constants import TILES_VERTICAL

        # Convert from bottom-up to top-down coordinates
        # tile_y is from bottom, so flip it
        screen_tile_y = TILES_VERTICAL - tile_y

        # Convert tile position to pixels (now in screen coordinates)
        pixel_x, pixel_y = tiles_to_pixels(tile_x, screen_tile_y)

        # Adjust Y for bottom alignment (draw from top of sprite)
        sprite_height = sprite.get_height()
        draw_y = pixel_y - sprite_height

        surface.blit(sprite, (pixel_x, draw_y))

    def preload_sprites(self, sheet_name, sprite_names=None):
        """Preload sprites into cache for faster access.

        Args:
            sheet_name: Name of the sprite sheet
            sprite_names: List of sprite names to preload, or None for all
        """
        if sheet_name not in SPRITE_SHEETS:
            return

        sprites_to_load = sprite_names or SPRITE_SHEETS[sheet_name].keys()

        for sprite_name in sprites_to_load:
            self.get(sheet_name, sprite_name)

        print(f"Preloaded {len(sprites_to_load)} sprites from {sheet_name}")


# Global sprite manager instance
sprites = SpriteManager()