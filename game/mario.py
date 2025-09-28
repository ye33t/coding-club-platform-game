"""Mario character management with intent-based architecture."""

import pygame
from dataclasses import dataclass
from .sprites import sprites
from .constants import FPS


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
    frame_timer: float = 0.0


class Mario:
    """Manages Mario's input processing and rendering."""

    def __init__(self, initial_state: MarioState = None):
        """Initialize Mario with a given state."""
        self.state = initial_state or MarioState()
        self.size = "small"  # small, big, fire

        # Animation configurations
        self.animations = {
            "idle": {
                "sprites": ["small_mario_stand"],
                "frame_duration": 1.0,
                "loop": True
            },
            "walking": {
                "sprites": ["small_mario_walk1", "small_mario_walk2"],
                "frame_duration": 6 / FPS,
                "loop": True
            },
            "running": {
                "sprites": ["small_mario_run1", "small_mario_run2"],
                "frame_duration": 3 / FPS,
                "loop": True
            },
            "jumping": {
                "sprites": ["small_mario_jump1", "small_mario_jump2", "small_mario_jump3",
                           "small_mario_jump4", "small_mario_jump5"],
                "frame_duration": 4 / FPS,
                "loop": False
            },
            "skidding": {
                "sprites": ["small_mario_skid"],
                "frame_duration": 1.0,
                "loop": True
            },
            "dying": {
                "sprites": ["small_mario_die"],
                "frame_duration": 1.0,
                "loop": False
            }
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
            new_state.frame_timer = 0.0

        self.state = new_state

    def update_animation(self, dt: float):
        """Update animation timer and frame."""
        if self.state.action not in self.animations:
            return

        anim = self.animations[self.state.action]

        # Update timer
        self.state.frame_timer += dt

        # Check if we need to advance frame
        if self.state.frame_timer >= anim["frame_duration"]:
            self.state.frame_timer = 0.0

            if anim["loop"]:
                # Loop animation
                self.state.frame = (self.state.frame + 1) % len(anim["sprites"])
            else:
                # Don't loop, stop at last frame
                if self.state.frame < len(anim["sprites"]) - 1:
                    self.state.frame += 1

    def draw(self, surface):
        """Draw Mario at current state."""
        sprite_name = self._get_sprite_name()
        if sprite_name:
            # Flip x coordinate if facing left
            draw_x = int(self.state.x)
            if not self.state.facing_right:
                # TODO: Add sprite flipping support
                pass

            sprites.draw_at_position(surface, "characters", sprite_name,
                                   draw_x, int(self.state.y))

    def _get_sprite_name(self) -> str:
        """Get the current sprite name based on state."""
        if self.state.action not in self.animations:
            return f"{self.size}_mario_stand"

        anim = self.animations[self.state.action]
        sprites = anim["sprites"]

        # Ensure frame is valid
        frame = min(self.state.frame, len(sprites) - 1)

        return sprites[frame]