# NES Platform Game - Learn Game Programming

A 2D platform game where you'll learn how video games really work.

## Setup

```bash
# Install dependencies
poetry install

# Run the game
poetry run game

# Format and lint code
poetry run format
```

## Animated Tiles

Terrain and background tiles now support simple sprite animations. In your tile
TOML, keep the existing `sprite` field for static tiles, or supply a `sprites`
array where each entry specifies the sprite name and how many frames it should
display:

```toml
[[tiles]]
slug = "item_box"
sprite_sheet = "item_box"
sprites = [
    { sprite = "item_box_1", frames = 6 },
    { sprite = "item_box_2", frames = 6 },
    { sprite = "item_box_3", frames = 6 },
]
collision_mask = "full"
```

The animation clock advances once per world update, so a `frames` value of 6
shows the sprite for roughly one tenth of a second at 60 FPS.
