"""End level state - Mario descending flagpole."""

from typing import TYPE_CHECKING

from ..physics.config import FLAGPOLE_DESCENT_SPEED
from .base import State

if TYPE_CHECKING:
    from ..game import Game


class EndLevelState(State):
    """State for Mario descending the flagpole.

    This state:
    - Locks Mario's X position to the flagpole center
    - Descends Mario at constant speed
    - Transitions to StartLevelState when Mario reaches the base
    """

    def __init__(self, flagpole_x: float, flagpole_base_y: float):
        """Initialize end level state.

        Args:
            flagpole_x: X pixel position (center of flagpole)
            flagpole_base_y: Y pixel position of base block top
        """
        self.flagpole_x = flagpole_x
        self.flagpole_base_y = flagpole_base_y

    def on_enter(self, game: "Game") -> None:
        """Lock Mario to flagpole position."""
        # Lock Mario's X position to flagpole center
        game.world.mario.state.x = self.flagpole_x
        # Stop horizontal movement
        game.world.mario.state.vx = 0

    def handle_events(self, game: "Game") -> None:
        """No input during flagpole descent."""
        pass

    def update(self, game: "Game", dt: float) -> None:
        """Descend Mario down the flagpole."""
        mario = game.world.mario

        # Move Mario down at constant speed
        mario.state.y -= FLAGPOLE_DESCENT_SPEED * dt

        # Update Mario's animation
        mario.update_animation()

        # Check if Mario has reached the base
        if mario.state.y <= self.flagpole_base_y:
            # Transition to start level with screen fade
            from .screen_transition import ScreenTransitionState, TransitionMode
            from .start_level import StartLevelState

            game.transition_to(
                ScreenTransitionState(self, StartLevelState(), TransitionMode.BOTH)
            )

    def draw(self, game: "Game", surface) -> None:
        """Draw Mario descending flagpole."""
        game._draw_level(surface)
        game._draw_mario(surface)
