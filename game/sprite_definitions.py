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
    "small_mario_skid": (76, 24, 2, 2),
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
}

ENEMIES = {
    # Goomba (2x2 tile space)
    "goomba_walk1": (0, 16, 2, 2),
}

BACKGROUND = {
    # Terrain
    "ground": (0, 32, 2, 2),
    "brick_top": (17, 32, 2, 2),
    "brick": (34, 32, 2, 2),
    "block_flat": (51, 32, 2, 2),
    "battlement": (68, 32, 2, 2),
    "battlement_1": (85, 32, 2, 2),
    "arch_center": (102, 32, 2, 2),
    "cannon_top": (119, 32, 2, 2),
    "block": (0, 49, 2, 2),
    "earth": (17, 49, 2, 2),
    "bridge": (34, 49, 2, 2),
    "arch_left": (51, 49, 2, 2),
    # "brick": (68, 49, 2, 2),
    "arch_right": (85, 49, 2, 2),
    "void": (102, 49, 2, 2),
    "cannon_center": (119, 49, 2, 2),
    "rocks": (0, 66, 2, 2),
    "conveyor_corner_left": (17, 66, 2, 2),
    "conveyor_horizontal": (34, 66, 2, 2),
    "conveyor_right": (51, 66, 2, 2),
    "sand_wave": (68, 66, 2, 2),
    "sand_lines": (85, 66, 2, 2),
    "cannon_bottom": (119, 66, 2, 2),
    "floating_blocks": (85, 84, 5, 3),
    "beanstalk": (0, 83, 2, 2),
    "ladder": (17, 83, 2, 2),
    "conveyor_vertical": (34, 83, 2, 2),
    "sand": (51, 83, 2, 2),
    "sand_dune": (68, 83, 2, 2),
    
    # Decorations
    "treetop_left": (0, 212, 2, 2),
    "treetop_center": (17, 212, 2, 2),
    "treetop_right": (34, 212, 2, 2),
    "mushroom_left": (51, 212, 2, 2),
    "mushroom_center": (68, 212, 2, 2),
    "mushroom_right": (85, 212, 2, 2),
    "lollipop_top": (102, 212, 2, 2),
    "pipe_mouth_left": (119, 212, 2, 2),
    "pipe_mouth_right": (136, 212, 2, 2),
    "bush_left": (0, 229, 2, 2),
    "bush_center": (17, 229, 2, 2),
    "bush_right": (34, 229, 2, 2),
    "leaves": (51, 229, 2, 2),
    "lollipop": (85, 229, 2, 2),
    "lollipop_bottom": (102, 229, 2, 2),
    "pipe_left": (119, 229, 2, 2),
    "pipe_right": (136, 229, 2, 2),
    "bridge_rails": (0, 246, 2, 2),
    #"sprite_18": (17, 246, 2, 2),
    "mound_top": (34, 246, 2, 2),
    "pipe_horizontal_mouth_top": (85, 246, 2, 2),
    "pipe_horizontal_top": (102, 246, 2, 2),
    "pipe_junction_top": (119, 246, 2, 2),
    "flagpole_top": (136, 246, 2, 2),
    "mound_left_45": (0, 263, 2, 2),
    "mound_left": (17, 263, 2, 2),
    "mound_center": (34, 263, 2, 2),
    "mound_right": (51, 263, 2, 2),
    "mound_right_45": (68, 263, 2, 2),
    "pipe_horizontal_mouth_bottom": (85, 263, 2, 2),
    "pipe_horizontal_bottom": (102, 263, 2, 2),
    "pipe_junction_bottom": (119, 263, 2, 2),
    "flagpole": (136, 263, 2, 2),
    
    # Clouds
    "cloud_top_left": (298, 32, 2, 2),
    "cloud_top": (315, 32, 2, 2),
    "cloud_top_right": (332, 32, 2, 2),
    "water_top": (349, 32, 2, 2),
    "cloud_block": (366, 32, 2, 2),
    "cloud_bottom_left": (298, 49, 2, 2),
    "cloud_bottom": (315, 49, 2, 2),
    "cloud_bottom_right": (332, 49, 2, 2),
    "water": (349, 49, 2, 2),
    "piano": (366, 49, 2, 2),
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
