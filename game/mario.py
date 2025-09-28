"""Mario character management with intent-based architecture."""

from copy import deepcopy
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

    # Dimensions (in pixels)
    width: float = 16.0  # 2 tiles wide
    height: float = 16.0  # 2 tiles tall

    # Status
    facing_right: bool = True
    on_ground: bool = True

    # Death state
    is_dying: bool = False
    death_leap_velocity: float = 0.0  # Initial upward velocity for death animation

    # Animation state
    action: str = "idle"  # idle, walking, running, jumping, skidding, dying
    frame: int = 0
    animation_length: int = 1  # Total frames in current animation

    # Input tracking
    input_duration: int = 0  # Frames current direction has been held

    def clone(self):
        """Create a deep copy of this state."""
        return deepcopy(self)

    def get_animation_progress(self) -> float:
        """Get the current animation progress as a percentage (0.0 to 1.0)."""
        if self.animation_length <= 1:
            return 1.0
        return self.frame / (self.animation_length - 1)


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

    def get_intent(self, keys) -> MarioIntent:
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
        # Check if action changed
        if new_state.action != self.state.action:
            # Set animation length for the new action
            if new_state.action in self.animations:
                new_state.animation_length = len(
                    self.animations[new_state.action]["sprites"]
                )
            else:
                new_state.animation_length = 1
            new_state.frame = 0

        # Also reset walking/running animations when changing direction while moving
        elif new_state.action in ["walking", "running"] and self.state.action in [
            "walking",
            "running",
        ]:
            # Reset if direction changed
            if (new_state.vx > 0) != (self.state.vx > 0) and abs(new_state.vx) > 1.0:
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
            # Use reflection when facing left
            draw_x = int(self.state.x)
            reflected = not self.state.facing_right

            sprites.draw_at_position(
                surface, "characters", sprite_name, draw_x, int(self.state.y), reflected
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
