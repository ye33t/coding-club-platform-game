"""Mario character management with intent-based architecture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import pygame
from pygame import Surface

from game.constants import TILE_SIZE
from game.physics.config import MARIO_TRANSITION_DURATION, MARIO_TRANSITION_INTERVAL

from .camera import Camera
from .content import sprites
from .rendering.base import Drawable


@dataclass
class MarioIntent:
    """What Mario wants to do based on input."""

    move_left: bool = False
    move_right: bool = False
    run: bool = False
    jump: bool = False
    duck: bool = False


@dataclass
class MarioTransition:
    """Represents an in-progress transition (e.g., size change)."""

    from_action: Callable[["Mario"], None]
    to_action: Callable[["Mario"], None]
    time_remaining: float = MARIO_TRANSITION_DURATION
    toggle_time: float = 0.0
    show_target: bool = True

    def update(self, dt: float, mario: "Mario") -> None:
        self.time_remaining -= dt
        if self.time_remaining > 0:
            # Update toggle timer
            self.toggle_time += dt

            # Toggle visibility at specified interval
            if self.toggle_time >= MARIO_TRANSITION_INTERVAL:
                self.toggle_time = 0.0
                self.show_target = not self.show_target

            # Apply the appropriate state
            if self.show_target:
                self.to_action(mario)
            else:
                self.from_action(mario)
        else:
            # Transition complete - apply final state
            self.show_target = True
            self.to_action(mario)
            mario.transition = None


class Mario(Drawable):
    """Manages Mario's input processing and rendering."""

    def __init__(self, x: float, y: float, screen: int):
        """Initialize Mario at specific coordinates.

        Args:
            x: X position in world pixels
            y: Y position in screen-relative pixels (0-224, from bottom)
            screen: Which vertical screen Mario is on
        """
        self.z_index = 20  # Render in front of effects and entities by default

        # Core mutable state (mutated directly by the physics pipeline)
        self.reset(x, y, screen)

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
                "stomping": {
                    "sprites": ["small_mario_stomp1"],
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
                "stomping": {
                    "sprites": ["big_mario_stomp1"],
                    "loop": True,
                },
                "skidding": {
                    "sprites": ["big_mario_skid"],
                    "loop": True,
                },
                "crouching": {
                    "sprites": ["big_mario_crouch"],
                    "loop": True,
                },
            },
        }

    def reset(self, x: float, y: float, screen: int) -> None:
        """Reset Mario to a baseline state at the given position."""
        # Position and physics
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.screen = screen

        # Dimensions (in pixels)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        # Status
        self.facing_right = True
        self.on_ground = True
        self.is_jumping = False  # True when in a player-initiated jump
        self.size = "small"  # small, big, fire
        self.transition: Optional[MarioTransition] = None

        # Animation state
        self.action = (
            "idle"  # idle, walking, running, jumping, skidding, dying, stomping
        )
        self.is_stomping = False  # True when falling toward an enemy
        self.frame = 0
        self.animation_length = 1  # Total frames in current animation
        self.animation_progress = 0.0  # Fractional progress for smooth cycling
        self._last_action = self.action
        self._last_size = self.size
        self._last_vx = self.vx
        self.intent = MarioIntent()
        self.visible = True

    def get_animation_progress(self) -> float:
        """Get the current animation progress as a percentage (0.0 to 1.0)."""
        if self.animation_length <= 1:
            return 1.0
        return self.frame / (self.animation_length - 1)

    def grow(self) -> None:
        """Trigger small-to-big transformation if Mario is small."""
        if self.size == "big":
            return

        self.transition = MarioTransition(
            from_action=self._small_action, to_action=self._big_action
        )

    def shrink(self) -> None:
        """Trigger big-to-small transformation if Mario is big."""
        if self.size == "small":
            return

        self.transition = MarioTransition(
            from_action=self._big_action, to_action=self._small_action
        )

    @property
    def is_invincible(self) -> bool:
        """Check if Mario is invincible (during transition)."""
        return self.transition is not None or self.action == "stomping"

    @staticmethod
    def _small_action(mario: "Mario") -> None:
        mario.size = "small"
        mario.width = TILE_SIZE
        mario.height = TILE_SIZE

    @staticmethod
    def _big_action(mario: "Mario") -> None:
        mario.size = "big"
        mario.width = TILE_SIZE
        mario.height = TILE_SIZE * 2

    def _update_animation(self) -> None:
        """Update animation metadata and advance frames for the current state."""
        current_animations = self.animations.get(self.size, self.animations["small"])

        sprites = current_animations.get(self.action)

        if self.action != self._last_action or self.size != self._last_size:
            self.animation_length = len(sprites) if sprites else 1
            self.frame = 0
            self.animation_progress = 0.0
        elif (
            self.action in ["walking", "running"]
            and self._last_action in ["walking", "running"]
            and (self.vx > 0) != (self._last_vx > 0)
            and abs(self.vx) > 1.0
        ):
            self.frame = 0
            self.animation_progress = 0.0

        if not sprites:
            self._last_action = self.action
            self._last_size = self.size
            self._last_vx = self.vx
            return

        if self.action in ["walking", "running"]:
            from .physics.config import ANIMATION_SPEED_SCALE, WALK_SPEED

            speed = abs(self.vx)
            frame_advance = (speed / WALK_SPEED) * ANIMATION_SPEED_SCALE

            self.animation_progress += frame_advance
            self.frame = int(self.animation_progress) % len(sprites)
        else:
            self.frame += 1
            if self.frame >= len(sprites):
                if current_animations[self.action]["loop"]:
                    self.frame = 0
                else:
                    self.frame = len(sprites) - 1

        self._last_action = self.action
        self._last_size = self.size
        self._last_vx = self.vx

    def update_intent(self, keys) -> None:
        """Process raw input and update the stored intent."""
        self.intent.move_right = keys[pygame.K_d]
        self.intent.move_left = not self.intent.move_right and keys[pygame.K_a]
        self.intent.run = keys[pygame.K_j]
        self.intent.jump = keys[pygame.K_k]
        self.intent.duck = not self.intent.jump and keys[pygame.K_s]

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Draw Mario at current state.

        Args:
            surface: Surface to draw on
            camera: Camera for coordinate transformation
        """
        if not self.visible:
            return

        self._update_animation()

        sprite_name = self._get_sprite_name()
        if sprite_name:
            # Transform Mario's world position to screen position
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)

            # Use reflection when facing left
            reflected = not self.facing_right

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
        current_animations = self.animations.get(self.size, self.animations["small"])

        if self.action not in current_animations:
            return f"{self.size}_mario_stand"

        anim = current_animations[self.action]
        sprite_list: List[str] = anim["sprites"]

        # Ensure frame is valid
        frame = min(self.frame, len(sprite_list) - 1)

        return sprite_list[frame]
