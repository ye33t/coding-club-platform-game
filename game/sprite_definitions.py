"""Sprite definitions with coordinates for each sprite sheet."""

# Sprite definitions format:
# "sprite_name": (x, y, actual_width, actual_height, tile_width, tile_height)
# x, y = pixel position on sprite sheet
# actual_width, actual_height = actual sprite pixel dimensions to extract
# tile_width, tile_height = logical tile space the sprite occupies in game

CHARACTERS = {
    # Small Mario (2x2 tile space)
    "small_mario_stand": (1, 9, 12, 16, 2, 2),
}

BLOCKS = {
    # Ground blocks (2x2 tile space, actual size 16x16)
    "ground_top": (0, 0, 16, 16, 2, 2),
}

ENEMIES = {
    # Goomba (2x2 tile space)
    "goomba_walk1": (0, 4, 16, 16, 2, 2),
}

BACKGROUND = {
    # Clouds
    "cloud_small": (0, 0, 32, 23, 4, 3),
}

OTHER = {
    # Power-ups (2x2 tile space)
    "mushroom": (0, 0, 16, 16, 2, 2),
}

# Map sheet names to their definitions
SPRITE_SHEETS = {
    "characters": CHARACTERS,
    "blocks": BLOCKS,
    "enemies": ENEMIES,
    "background": BACKGROUND,
    "other": OTHER,
}