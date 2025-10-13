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

    def update(self, game: "Game", dt: float) -> None:
        """Immediately transition to start level with fade-in."""

        from ..rendering import TransitionMode
        from .start_level import StartLevelState

        game.start_transition(StartLevelState(), TransitionMode.FADE_IN)
