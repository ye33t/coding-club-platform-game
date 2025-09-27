"""Sprite definitions with coordinates for each sprite sheet."""

# Sprite definitions format:
# "sprite_name": (x, y, tile_width, tile_height)
# x, y = pixel position on sprite sheet where the bottom-left coordinate is located,
#        (0,0) is the top-left of the image
# tile_width, tile_height = the size of the sprite in tile coordinates

CHARACTERS = {
    # Small Mario (2x2 tile space)
    "small_mario_stand": (0, 24, 2, 2),
}

BLOCKS = {
    # Ground blocks (2x2 tile space, actual size 16x16)
    "ground_top": (0, 16, 2, 2),
}

ENEMIES = {
    # Goomba (2x2 tile space)
    "goomba_walk1": (0, 16, 2, 2),
}

BACKGROUND = {
    # Clouds
    "cloud_small": (0, 32, 4, 3),
}

OTHER = {
    # Power-ups (2x2 tile space)
    "mushroom": (0, 16, 2, 2),
}

# Map sheet names to their definitions
SPRITE_SHEETS = {
    "characters": CHARACTERS,
    "blocks": BLOCKS,
    "enemies": ENEMIES,
    "background": BACKGROUND,
    "other": OTHER,
}