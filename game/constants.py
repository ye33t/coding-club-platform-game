"""NES-style game constants and specifications."""

# NES NTSC display specifications
NATIVE_WIDTH = 256  # NES horizontal resolution
NATIVE_HEIGHT = 224  # NES NTSC vertical resolution
TILE_SIZE = 8  # NES uses 8x8 pixel tiles
TILES_HORIZONTAL = NATIVE_WIDTH // TILE_SIZE  # 32 tiles
TILES_VERTICAL = NATIVE_HEIGHT // TILE_SIZE  # 28 tiles

# Display scaling
DEFAULT_SCALE = 3  # 3x scaling (768x672 window)
MIN_SCALE = 1
MAX_SCALE = 6

# Timing
FPS = 60  # NES runs at ~60 FPS (actually 60.0988 for NTSC)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TRANSPARENT = (0, 41, 140)  # Dark blue transparency color

# NES-style dark gray background (similar to NES palette entry $00)
BACKGROUND_COLOR = (146, 144, 255)


# Coordinate conversion helpers
def tiles_to_pixels(tile_x, tile_y):
    """Convert tile coordinates to pixel coordinates."""
    return tile_x * TILE_SIZE, tile_y * TILE_SIZE


def pixels_to_tiles(pixel_x, pixel_y):
    """Convert pixel coordinates to tile coordinates (integer division)."""
    return pixel_x // TILE_SIZE, pixel_y // TILE_SIZE


def pixels_to_tile_size(pixel_width, pixel_height):
    """Convert pixel dimensions to tile dimensions (rounds up)."""
    tile_width = (pixel_width + TILE_SIZE - 1) // TILE_SIZE
    tile_height = (pixel_height + TILE_SIZE - 1) // TILE_SIZE
    return tile_width, tile_height
