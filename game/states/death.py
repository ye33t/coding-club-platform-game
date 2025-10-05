"""Death state - Mario death animation and reset."""

from typing import TYPE_CHECKING

from ..camera import CameraState
from ..mario import MarioState
from ..physics.config import DEATH_LEAP_VELOCITY, GRAVITY, RESET_THRESHOLD_Y
from .base import State

if TYPE_CHECKING:
    from ..game import Game


class DeathState(State):
    """State for animating Mario's death and resetting the game.

    This state:
    - Gives Mario an upward leap
    - Applies gravity to make him fall
    - Resets Mario to spawn point when he falls far enough
    - Transitions back to PlayingState
    """

    def on_enter(self, game: "Game") -> None:
        """Initialize death animation."""
        # Give Mario the death leap velocity
        game.world.mario.state.vy = DEATH_LEAP_VELOCITY
        game.world.mario.state.vx = 0
        
        # Tells the renderer what animation to use for Mario
        game.world.mario.state.action = "dying"

    def handle_events(self, game: "Game") -> None:
        """No input during death."""
        pass

    def update(self, game: "Game", dt: float) -> None:
        """Update death animation."""
        mario = game.world.mario

        # Apply gravity
        mario.state.vy -= GRAVITY * dt

        # Update position
        mario.state.y += mario.state.vy * dt

        # Update animation
        mario.update_animation()

        # Check if Mario has fallen far enough to reset
        if mario.state.y < RESET_THRESHOLD_Y:
            # Reset Mario to spawn point
            mario.state = MarioState(
                x=game.world.level.spawn_x,
                y=game.world.level.spawn_y,
                screen=game.world.level.spawn_screen,
            )

            # Reset camera to beginning (both position and ratchet)
            game.world.camera.state = CameraState(x=0, max_x=0)

            # Transition back to playing
            from .playing import PlayingState

            game.transition_to(PlayingState())

    def draw(self, game: "Game", surface) -> None:
        """Draw Mario during death animation."""
        game._draw_level(surface)
        game._draw_mario(surface)
