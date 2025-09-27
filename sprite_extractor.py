#!/usr/bin/env python3
"""Semi-automated sprite extraction tool for sprite sheets."""

import math
import pygame
import sys
from collections import deque

# Colors to ignore
TRANSPARENT_BLUE = (0, 41, 140)
WHITE = (255, 255, 255)
IGNORE_COLORS = [TRANSPARENT_BLUE, WHITE]

def extract_sprites_from_region(sheet_path, x1, y1, x2, y2):
    """
    Extract sprites from a specific region of a sprite sheet.

    Args:
        sheet_path: Path to the sprite sheet image
        x1, y1: Top-left corner of search region
        x2, y2: Bottom-right corner of search region

    Returns:
        List of sprite definitions (x_bottom, y_bottom, width_tiles, height_tiles)
    """
    # Initialize pygame to load images
    pygame.init()

    # Load the sprite sheet
    try:
        sheet = pygame.image.load(sheet_path)
    except pygame.error as e:
        print(f"Error loading sprite sheet: {e}")
        return []

    # Get sheet dimensions
    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()

    # Validate region bounds
    x1 = max(0, min(x1, sheet_width))
    x2 = max(x1, min(x2, sheet_width))
    y1 = max(0, min(y1, sheet_height))
    y2 = max(y1, min(y2, sheet_height))

    # Create a visited array
    visited = [[False] * sheet_width for _ in range(sheet_height)]

    # List to store found sprites
    sprites = []

    def is_valid_pixel(x, y):
        """Check if a pixel should be considered part of a sprite."""
        if x < 0 or x >= sheet_width or y < 0 or y >= sheet_height:
            return False
        pixel = sheet.get_at((x, y))[:3]  # Get RGB, ignore alpha
        return pixel not in IGNORE_COLORS

    def flood_fill(start_x, start_y):
        """Find all connected pixels starting from a point."""
        min_x, max_x = start_x, start_x
        min_y, max_y = start_y, start_y

        queue = deque([(start_x, start_y)])
        visited[start_y][start_x] = True

        while queue:
            x, y = queue.popleft()

            # Update bounds
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

            # Check 4-connected neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx >= x1 and nx < x2 and ny >= y1 and ny < y2 and
                    not visited[ny][nx] and is_valid_pixel(nx, ny)):
                    visited[ny][nx] = True
                    queue.append((nx, ny))

        return min_x, min_y, max_x, max_y

    # Scan the region for sprites
    for y in range(y1, y2):
        for x in range(x1, x2):
            if not visited[y][x] and is_valid_pixel(x, y):
                # Found a new sprite, flood fill to find its bounds
                min_x, min_y, max_x, max_y = flood_fill(x, y)

                # Calculate sprite dimensions
                pixel_width = max_x - min_x + 1
                pixel_height = max_y - min_y + 1

                # Skip very small regions (likely noise)
                if pixel_width < 4 or pixel_height < 4:
                    continue

                # Calculate bottom-left position
                bottom_left_x = min_x
                bottom_left_y = max_y + 1  # One pixel below the bottom edge

                # Calculate tile dimensions (round up)
                width_tiles = math.ceil(pixel_width / 8)
                height_tiles = math.ceil(pixel_height / 8)

                sprites.append((bottom_left_x, bottom_left_y, width_tiles, height_tiles))

    return sprites


def print_sprite_definitions(sprites, prefix="sprite"):
    """Print sprite definitions in Python dictionary format."""
    print("\n# Extracted sprite definitions:")
    for i, (x, y, w, h) in enumerate(sprites):
        print(f'    "{prefix}_{i}": ({x}, {y}, {w}, {h}),')


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python sprite_extractor.py <sprite_sheet.png> [x1 y1 x2 y2]")
        print("If no region specified, scans entire image")
        sys.exit(1)

    sheet_path = sys.argv[1]

    # Parse region if provided
    if len(sys.argv) >= 6:
        x1 = int(sys.argv[2])
        y1 = int(sys.argv[3])
        x2 = int(sys.argv[4])
        y2 = int(sys.argv[5])
    else:
        # Use full image
        pygame.init()
        sheet = pygame.image.load(sheet_path)
        x1, y1 = 0, 0
        x2 = sheet.get_width()
        y2 = sheet.get_height()

    print(f"Extracting sprites from {sheet_path}")
    print(f"Region: ({x1}, {y1}) to ({x2}, {y2})")
    print(f"Ignoring colors: {IGNORE_COLORS}")

    sprites = extract_sprites_from_region(sheet_path, x1, y1, x2, y2)

    print(f"\nFound {len(sprites)} sprites:")
    print_sprite_definitions(sprites)

    # Also print pixel info for verification
    print("\n# Pixel dimensions (for reference):")
    for i, (x, y, w, h) in enumerate(sprites):
        pixel_w = w * 8
        pixel_h = h * 8
        print(f"# sprite_{i}: {pixel_w}x{pixel_h} pixels at ({x}, {y})")


if __name__ == "__main__":
    main()