"""Death state - Mario death animation."""

from typing import TYPE_CHECKING

from ..physics.config import DEATH_LEAP_VELOCITY, GRAVITY, RESET_THRESHOLD_Y
from .base import State

if TYPE_CHECKING:
    from ..game import Game


class DeathState(State):
    """State for animating Mario's death.

    This state:
    - Gives Mario an upward leap
    - Applies gravity to make him fall
    - Transitions to StartLevelState when animation is complete
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

        # Check if Mario has fallen far enough to end animation
        if mario.state.y < RESET_THRESHOLD_Y:
            # Transition to start level with screen fade
            from .screen_transition import ScreenTransitionState
            from .start_level import StartLevelState

            game.transition_to(ScreenTransitionState(self, StartLevelState()))

    def draw(self, game: "Game", surface) -> None:
        """Draw Mario during death animation."""
        game.draw_background(surface)
        game.draw_terrain(surface)
        game.draw_mario(surface)
