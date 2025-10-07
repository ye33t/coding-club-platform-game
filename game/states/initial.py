"""Initial state - black screen before game starts."""

from typing import TYPE_CHECKING

from ..constants import BACKGROUND_COLOR
from .base import State

if TYPE_CHECKING:
    from ..game import Game


class InitialState(State):
    """Initial black screen state.

    Draws a black screen and immediately transitions to StartLevelState
    with a fade-in effect.
    """

    def handle_events(self, game: "Game") -> None:
        """No events during initial state."""
        pass

    def update(self, game: "Game", dt: float) -> None:
        """Immediately transition to start level with fade-in."""
        from .screen_transition import ScreenTransitionState, TransitionMode
        from .start_level import StartLevelState

        game.transition_to(
            ScreenTransitionState(self, StartLevelState(), TransitionMode.FADE_IN)
        )

    def draw(self, game: "Game", surface) -> None:
        """Draw black screen."""
        surface.fill(BACKGROUND_COLOR)
