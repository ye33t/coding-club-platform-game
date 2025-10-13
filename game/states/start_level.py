"""Start level state - positions Mario and initializes level."""

from .base import State


class StartLevelState(State):
    """State for starting or restarting a level.

    This state:
    - Positions Mario at the level's spawn point
    - Resets camera to origin
    - Immediately transitions to PlayingState
    """

    def on_enter(self, game) -> None:
        """Initialize level start."""
        game.world.reset()

    def handle_events(self, game) -> None:
        """No events during instant transition."""
        pass

    def update(self, game, dt: float) -> None:
        # Immediately transition to playing
        from .playing import PlayingState

        game.transition_to(PlayingState())

    def draw(self, game, surface) -> None:
        """Draw the initial state."""
        game.draw_world(surface)
