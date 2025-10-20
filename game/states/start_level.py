"""Start level state - positions Mario and initializes level."""

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..game import Game


class StartLevelState(State):
    """State for starting or restarting a level.

    This state:
    - Positions Mario at the level's spawn point
    - Resets camera to origin
    - Immediately transitions to PlayingState
    """

    def __init__(self, preserve_progress: bool = False) -> None:
        self._preserve_progress = preserve_progress

    def on_enter(self, game: "Game") -> None:
        """Initialize level start."""
        game.world.reset(preserve_progress=self._preserve_progress)

    def update(self, game: "Game", dt: float) -> None:
        # Immediately transition to playing
        from .playing import PlayingState

        game.transition(PlayingState())
