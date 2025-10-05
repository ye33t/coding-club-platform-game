"""Start level state - positions Mario and initializes level."""

from typing import TYPE_CHECKING

from ..camera import CameraState
from ..mario import MarioState
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

    def on_enter(self, game: "Game") -> None:
        """Initialize level start."""
        # Reset Mario to spawn point
        game.world.mario.state = MarioState(
            x=game.world.level.spawn_x,
            y=game.world.level.spawn_y,
            screen=game.world.level.spawn_screen,
        )

        # Reset camera to beginning (both position and ratchet)
        game.world.camera.state = CameraState(x=0, max_x=0)

    def handle_events(self, game: "Game") -> None:
        """No events during instant transition."""
        pass

    def update(self, game: "Game", dt: float) -> None:
        # Immediately transition to playing
        from .playing import PlayingState

        game.transition_to(PlayingState())

    def draw(self, game: "Game", surface) -> None:
        """Draw the initial state."""
        game._draw_level(surface)
        game._draw_mario(surface)
