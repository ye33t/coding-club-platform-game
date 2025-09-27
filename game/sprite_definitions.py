"""Sprite definitions with coordinates for each sprite sheet."""

# Sprite definitions format:
# "sprite_name": (x, y, tile_width, tile_height)
# x, y = pixel position on sprite sheet where the bottom-left coordinate is located,
#        (0,0) is the top-left of the image
# tile_width, tile_height = the size of the sprite in tile coordinates

CHARACTERS = {
    # Small Mario (2x2 tile space)
    "small_mario_stand": (0, 24, 2, 2),
    "small_mario_walk1": (20, 24, 2, 2),
    "small_mario_walk2": (38, 24, 2, 2),
    "small_mario_run1": (56, 24, 2, 2),
    "small_mario_turn": (76, 24, 2, 2),
    "small_mario_run2": (96, 24, 2, 2),
    "small_mario_die": (116, 24, 2, 2),
    "small_mario_bounce1": (136, 24, 2, 2),
    "small_mario_bounce2": (154, 24, 2, 2),
    "small_mario_jump1": (174, 24, 2, 2),
    "small_mario_jump2": (192, 24, 2, 2),
    "small_mario_jump3": (210, 24, 2, 2),
    "small_mario_jump4": (228, 24, 2, 2),
    "small_mario_jump5": (246, 24, 2, 2),
    # "circle": (264, 16, 1, 1),
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