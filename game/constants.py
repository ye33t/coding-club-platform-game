"""NES-style game constants and specifications."""

# NES NTSC display specifications
NATIVE_WIDTH = 256  # NES horizontal resolution
NATIVE_HEIGHT = 224  # NES NTSC vertical resolution

# Sub-tile size and counts
SUB_TILE_SIZE = 8  # NES uses 8x8 pixel tiles
SUB_TILES_HORIZONTAL = NATIVE_WIDTH // SUB_TILE_SIZE
SUB_TILES_VERTICAL = NATIVE_HEIGHT // SUB_TILE_SIZE

# Game tile size and counts
TILE_SIZE = 16  # Each game tile is 2x2 sub-tiles
TILES_HORIZONTAL = NATIVE_WIDTH // TILE_SIZE
TILES_VERTICAL = NATIVE_HEIGHT // TILE_SIZE

# Display scaling
DEFAULT_SCALE = 3  # 3x scaling (768x672 window)
MIN_SCALE = 1
MAX_SCALE = 6

# Timing
FPS = 60  # NES runs at ~60 FPS (actually 60.0988 for NTSC)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND_COLOR = TRANSPARENT = (146, 144, 255)  # Light purple (NES background color)

# Session defaults
INITIAL_LIVES = 3
COIN_LIFE_THRESHOLD = 100
LIFE_SPLASH_FRAMES = FPS * 3  # Display the life splash for three seconds by default
