"""Mario character management with intent-based architecture."""

from dataclasses import dataclass
from typing import Any, Dict, List

import pygame

from .sprites import sprites


def repeat(sprite: str, times: int) -> List[str]:
    """Helper to repeat a sprite n times in animation."""
    return [sprite] * times


@dataclass
class MarioIntent:
    """What Mario wants to do based on input."""

    move_left: bool = False
    move_right: bool = False
    run: bool = False
    jump: bool = False
    duck: bool = False


@dataclass
class MarioState:
    """Mario's actual state in the world."""

    # Position and physics
    x: float = 0.0
    y: float = 16.0  # Start 2 tiles from bottom
    vx: float = 0.0
    vy: float = 0.0

    # Status
    facing_right: bool = True
    on_ground: bool = True

    # Animation state
    action: str = "idle"  # idle, walking, running, jumping, skidding, dying
    frame: int = 0


class Mario:
    """Manages Mario's input processing and rendering."""

    def __init__(self, initial_state: MarioState):
        """Initialize Mario with a given state."""
        self.state = initial_state
        self.size = "small"  # small, big, fire

        # Animation configurations (each element = 1 frame at 60 FPS)
        self.animations: Dict[str, Dict[str, Any]] = {
            "idle": {
                "sprites": repeat("small_mario_stand", 60),  # Hold for 1 second
                "loop": True,
            },
            "walking": {
                "sprites": repeat("small_mario_walk1", 6)
                + repeat("small_mario_walk2", 6),  # 12 frames total
                "loop": True,
            },
            "running": {
                "sprites": repeat("small_mario_run1", 3)
                + repeat("small_mario_run2", 3),  # 6 frames total
                "loop": True,
            },
            "jumping": {
                "sprites": (
                    repeat("small_mario_jump1", 4)
                    + repeat("small_mario_jump2", 4)
                    + repeat("small_mario_jump3", 4)
                    + repeat("small_mario_jump4", 4)
                    + repeat("small_mario_jump5", 4)
                ),  # 20 frames total
                "loop": False,
            },
            "skidding": {
                "sprites": repeat("small_mario_skid", 12),  # Hold for 0.2 seconds
                "loop": True,
            },
            "dying": {
                "sprites": repeat("small_mario_die", 60),  # Hold for 1 second
                "loop": False,
            },
        }

    def read_input(self, keys) -> MarioIntent:
        """Process raw input into intent."""
        intent = MarioIntent()
        intent.move_left = keys[pygame.K_LEFT]
        intent.move_right = keys[pygame.K_RIGHT]
        intent.run = keys[pygame.K_LSHIFT]
        intent.jump = keys[pygame.K_SPACE]
        intent.duck = keys[pygame.K_DOWN]
        return intent

    def apply_state(self, new_state: MarioState):
        """Accept the authoritative state from the world."""
        # Check if action changed to reset animation
        if new_state.action != self.state.action:
            new_state.frame = 0

        self.state = new_state

    def update_animation(self):
        """Update animation frame (just increment, no timer needed)."""
        if self.state.action not in self.animations:
            return

        anim = self.animations[self.state.action]
        sprites = anim["sprites"]

        # Simply increment the frame
        self.state.frame += 1

        # Handle looping or stopping at end
        if self.state.frame >= len(sprites):
            if anim["loop"]:
                self.state.frame = 0
            else:
                self.state.frame = len(sprites) - 1

    def draw(self, surface):
        """Draw Mario at current state."""
        sprite_name = self._get_sprite_name()
        if sprite_name:
            # Flip x coordinate if facing left
            draw_x = int(self.state.x)
            if not self.state.facing_right:
                # TODO: Add sprite flipping support
                pass

            sprites.draw_at_position(
                surface, "characters", sprite_name, draw_x, int(self.state.y)
            )

    def _get_sprite_name(self) -> str:
        """Get the current sprite name based on state."""
        if self.state.action not in self.animations:
            return f"{self.size}_mario_stand"

        anim = self.animations[self.state.action]
        sprite_list: List[str] = anim["sprites"]

        # Ensure frame is valid
        frame = min(self.state.frame, len(sprite_list) - 1)

        return sprite_list[frame]
