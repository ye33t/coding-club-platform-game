"""Sprite sheet loading and extraction."""

import pygame

from .constants import SUB_TILE_SIZE


class SpriteSheet:
    """Handles loading and extracting sprites from a sprite sheet."""

    def __init__(self, filepath, colorkey=None):
        """Load a sprite sheet from file.

        Args:
            filepath: Path to the sprite sheet image
            colorkey: Color to treat as transparent (RGB tuple) or 'auto'
                for top-left pixel
        """
        self.sheet = pygame.image.load(filepath).convert()
        self.colorkey = colorkey
        self.sprite_cache = {}

        if colorkey == "auto":
            # Use top-left pixel as transparent color
            self.colorkey = self.sheet.get_at((0, 0))[:3]

        if self.colorkey:
            self.sheet.set_colorkey(self.colorkey)

    def get_sprite(self, x, y, tile_width, tile_height):
        """Extract a sprite from the sheet using bottom-left coordinates.

        Args:
            x: X coordinate of sprite's bottom-left corner in pixels
            y: Y coordinate of sprite's bottom-left corner in pixels
            tile_width: Width of the sprite in tiles
            tile_height: Height of the sprite in tiles

        Returns:
            pygame.Surface containing the sprite
        """
        # Calculate pixel dimensions
        width = tile_width * SUB_TILE_SIZE
        height = tile_height * SUB_TILE_SIZE

        # Calculate top-left corner from bottom-left
        top_left_x = x
        top_left_y = y - height

        # Use coordinates as cache key
        cache_key = (x, y, tile_width, tile_height)

        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]

        # Create surface for the sprite
        sprite = pygame.Surface((width, height))

        if self.colorkey:
            sprite.set_colorkey(self.colorkey)
            sprite.fill(self.colorkey)

        # Copy the sprite area from the sheet
        sprite.blit(self.sheet, (0, 0), (top_left_x, top_left_y, width, height))
        sprite = sprite.convert()

        # Cache the sprite
        self.sprite_cache[cache_key] = sprite

        return sprite
