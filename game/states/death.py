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

    def __init__(self) -> None:
        self._transition_started = False

    def on_enter(self, game: "Game") -> None:
        """Initialize death animation."""
        self._transition_started = False
        # Give Mario the death leap velocity
        game.world.mario.vy = DEATH_LEAP_VELOCITY
        game.world.mario.vx = 0

        # Tells the renderer what animation to use for Mario
        game.world.mario.size = "small"
        game.world.mario.action = "dying"

    def update(self, game: "Game", dt: float) -> None:
        """Update death animation."""
        mario = game.world.mario

        # Apply gravity
        mario.vy -= GRAVITY * dt

        # Update position
        mario.y += mario.vy * dt

        # Check if Mario has fallen far enough to end animation
        if mario.y < RESET_THRESHOLD_Y and not self._transition_started:
            # Transition to start level with screen fade
            from ..rendering import TransitionMode
            from .start_level import StartLevelState

            self._transition_started = True
            game.transition(StartLevelState(), TransitionMode.BOTH)
