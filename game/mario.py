"""Mario character management with intent-based architecture."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pygame

from game.constants import TILE_SIZE

from .content import sprites


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
    size: str = "small"  # small, big, fire
    power_up_transition: Optional[str] = None
    transition_from_size: Optional[str] = None
    transition_to_size: Optional[str] = None
    transition_time_remaining: float = 0.0
    transition_toggle_counter: int = 0
    transition_show_target: bool = True

    # Animation state
    action: str = "idle"  # idle, walking, running, jumping, skidding, dying
    frame: int = 0
    animation_length: int = 1  # Total frames in current animation
    animation_progress: float = 0.0  # Fractional progress for smooth cycling

    def clone(self):
        """Create a deep copy of this state."""
        return deepcopy(self)

    def get_animation_progress(self) -> float:
        """Get the current animation progress as a percentage (0.0 to 1.0)."""
        if self.animation_length <= 1:
            return 1.0
        return self.frame / (self.animation_length - 1)

    def set_size(self, size: str) -> None:
        """Update Mario's size and adjust hitbox dimensions."""
        self.size = size
        if size == "big":
            self.width = TILE_SIZE
            self.height = TILE_SIZE * 2
        else:
            self.width = TILE_SIZE
            self.height = TILE_SIZE


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
        self.z_index = 20  # Render in front of effects and entities by default

        # Animation configurations (each element = 1 frame at 60 FPS)
        self.animations: Dict[str, Dict[str, Dict[str, Any]]] = {
            "small": {
                "idle": {
                    "sprites": ["small_mario_stand"],
                    "loop": True,
                },
                "walking": {
                    # Use single frames - speed controlled by velocity
                    "sprites": [
                        "small_mario_walk1",
                        "small_mario_walk2",
                        "small_mario_walk3",
                    ],
                    "loop": True,
                },
                "running": {
                    # Same animation as walking - speed controlled by velocity
                    "sprites": [
                        "small_mario_walk1",
                        "small_mario_walk2",
                        "small_mario_walk3",
                    ],
                    "loop": True,
                },
                "jumping": {
                    # Single static jump frame
                    "sprites": ["small_mario_jump"],  # Hold entire jump
                    "loop": True,
                },
                "skidding": {
                    "sprites": ["small_mario_skid"],  # Hold for 0.2 seconds
                    "loop": True,
                },
                "dying": {
                    "sprites": ["small_mario_die"],  # Hold for 1 second
                    "loop": True,
                },
            },
            "big": {
                "idle": {
                    "sprites": ["big_mario_stand"],
                    "loop": True,
                },
                "walking": {
                    "sprites": [
                        "big_mario_walk1",
                        "big_mario_walk2",
                        "big_mario_walk3",
                    ],
                    "loop": True,
                },
                "running": {
                    "sprites": [
                        "big_mario_walk1",
                        "big_mario_walk2",
                        "big_mario_walk3",
                    ],
                    "loop": True,
                },
                "jumping": {
                    "sprites": ["big_mario_jump"],
                    "loop": True,
                },
                "skidding": {
                    "sprites": ["big_mario_skid"],
                    "loop": True,
                },
                "dying": {
                    "sprites": ["small_mario_die"],
                    "loop": True,
                },
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
        current_animations = self.animations.get(
            new_state.size, self.animations["small"]
        )

        previous_size = self.state.size
        if new_state.action != self.state.action or new_state.size != previous_size:
            # Set animation length for the new action using current size palette.
            if new_state.action in current_animations:
                new_state.animation_length = len(
                    current_animations[new_state.action]["sprites"]
                )
            else:
                new_state.animation_length = 1
            new_state.frame = 0
            # Reset animation progress for velocity-based animations
            new_state.animation_progress = 0.0

        # Also reset walking/running animations when changing direction while moving
        elif new_state.action in ["walking", "running"] and self.state.action in [
            "walking",
            "running",
        ]:
            # Reset if direction changed
            if (new_state.vx > 0) != (self.state.vx > 0) and abs(new_state.vx) > 1.0:
                new_state.frame = 0
                # Reset animation progress
                new_state.animation_progress = 0.0

        self.state = new_state

    def update_animation(self):
        """Update animation frame based on velocity for movement animations."""
        current_animations = self.animations.get(
            self.state.size, self.animations["small"]
        )

        if self.state.action not in current_animations:
            return

        anim = current_animations[self.state.action]
        sprites = anim["sprites"]

        # For movement animations, advance based on velocity
        if self.state.action in ["walking", "running"]:
            # Animation speed proportional to velocity
            # Scale linearly with actual velocity
            from .physics.config import ANIMATION_SPEED_SCALE, WALK_SPEED

            speed = abs(self.state.vx)
            frame_advance = (
                speed / WALK_SPEED
            ) * ANIMATION_SPEED_SCALE  # Normalized to walk speed

            # Use floating point for smooth animation
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

    def draw(self, surface, camera):
        """Draw Mario at current state.

        Args:
            surface: Surface to draw on
            camera: Camera for coordinate transformation
        """
        sprite_name = self._get_sprite_name()
        if sprite_name:
            # Transform Mario's world position to screen position
            screen_x, screen_y = camera.world_to_screen(self.state.x, self.state.y)

            # Use reflection when facing left
            reflected = not self.state.facing_right

            sprites.draw_at_position(
                surface,
                "characters",
                sprite_name,
                int(screen_x),
                int(screen_y),
                reflected,
            )

    def _get_sprite_name(self) -> str:
        """Get the current sprite name based on state."""
        current_animations = self.animations.get(
            self.state.size, self.animations["small"]
        )

        if self.state.action not in current_animations:
            return f"{self.state.size}_mario_stand"

        anim = current_animations[self.state.action]
        sprite_list: List[str] = anim["sprites"]

        # Ensure frame is valid
        frame = min(self.state.frame, len(sprite_list) - 1)

        return sprite_list[frame]
