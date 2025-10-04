"""Mario character management with intent-based architecture."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List

import pygame

from game.constants import TILE_SIZE

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
    y: float = 0.0  # Start 2 tiles from bottom (screen-relative: 0-224 pixels)
    vx: float = 0.0
    vy: float = 0.0
    screen: int = 0  # Which vertical screen Mario is on (-1, 0, 1, etc.)

    # Dimensions (in pixels)
    width: float = TILE_SIZE
    height: float = TILE_SIZE

    # Status
    facing_right: bool = True
    on_ground: bool = True
    is_jumping: bool = False  # True when in a player-initiated jump

    # Death state
    is_dying: bool = False
    death_leap_velocity: float = 0.0  # Initial upward velocity for death animation

    # Animation state
    action: str = "idle"  # idle, walking, running, jumping, skidding, dying
    frame: int = 0
    animation_length: int = 1  # Total frames in current animation

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

    def __init__(self, x: float, y: float, screen: int):
        """Initialize Mario at specific coordinates.

        Args:
            x: X position in world pixels
            y: Y position in screen-relative pixels (0-224, from bottom)
            screen: Which vertical screen Mario is on
        """
        self.state = MarioState(x=x, y=y, screen=screen)
        self.size = "small"  # small, big, fire

        # Animation configurations (each element = 1 frame at 60 FPS)
        self.animations: Dict[str, Dict[str, Any]] = {
            "idle": {
                "sprites": repeat("small_mario_stand", 60),  # Hold for 1 second
                "loop": True,
            },
            "walking": {
                # Use single frames - speed controlled by velocity
                "sprites": ["small_mario_walk1", "small_mario_walk2", "small_mario_walk3"],
                "loop": True,
            },
            "running": {
                # Same animation as walking - speed controlled by velocity
                "sprites": ["small_mario_walk1", "small_mario_walk2", "small_mario_walk3"],
                "loop": True,
            },
            "jumping": {
                # Single static jump frame
                "sprites": repeat("small_mario_jump", 1),  # Hold entire jump
                "loop": True,
            },
            "skidding": {
                "sprites": repeat("small_mario_skid", 1),  # Hold for 0.2 seconds
                "loop": True,
            },
            "dying": {
                "sprites": repeat("small_mario_die", 1),  # Hold for 1 second
                "loop": True,
            },
        }

    def get_intent(self, keys) -> MarioIntent:
        """Process raw input into intent."""
        intent = MarioIntent()
        intent.move_left = keys[pygame.K_a]
        intent.move_right = keys[pygame.K_d]
        intent.run = keys[pygame.K_j]
        intent.jump = keys[pygame.K_k]
        intent.duck = keys[pygame.K_s]
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
            # Reset animation progress for velocity-based animations
            if hasattr(self.state, 'animation_progress'):
                delattr(self.state, 'animation_progress')

        # Also reset walking/running animations when changing direction while moving
        elif new_state.action in ["walking", "running"] and self.state.action in [
            "walking",
            "running",
        ]:
            # Reset if direction changed
            if (new_state.vx > 0) != (self.state.vx > 0) and abs(new_state.vx) > 1.0:
                new_state.frame = 0
                # Reset animation progress
                if hasattr(self.state, 'animation_progress'):
                    delattr(self.state, 'animation_progress')

        self.state = new_state

    def update_animation(self):
        """Update animation frame based on velocity for movement animations."""
        if self.state.action not in self.animations:
            return

        anim = self.animations[self.state.action]
        sprites = anim["sprites"]

        # For movement animations, advance based on velocity
        if self.state.action in ["walking", "running"]:
            # Animation speed proportional to velocity
            # Scale linearly with actual velocity
            from .physics.config import ANIMATION_SPEED_SCALE
            speed = abs(self.state.vx)
            frame_advance = (speed / 85.0) * ANIMATION_SPEED_SCALE  # Normalized to walk speed

            # Use floating point for smooth animation
            if not hasattr(self.state, 'animation_progress'):
                self.state.animation_progress = 0.0

            self.state.animation_progress += frame_advance
            self.state.frame = int(self.state.animation_progress) % len(sprites)
        else:
            # Non-movement animations advance at fixed rate
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
