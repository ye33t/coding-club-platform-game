"""End level state - Mario descending flagpole."""

from game.constants import TILE_SIZE

from ..physics.config import FLAGPOLE_DESCENT_SPEED
from .base import State


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
        self._transition_started = False

    def on_enter(self, game) -> None:
        """Lock Mario to flagpole position."""
        # Lock Mario's X position to left of flagpole (offset by TILE_SIZE pixels)
        game.world.mario.x = self.flagpole_x - TILE_SIZE
        # Stop horizontal movement
        game.world.mario.vx = 0
        game.world.mario.facing_right = True

    def update(self, game, dt: float) -> None:
        """Descend Mario down the flagpole."""
        mario = game.world.mario

        # Move Mario down at constant speed
        mario.y -= FLAGPOLE_DESCENT_SPEED * dt

        # Clamp Mario's position at the base and flip him to the other side of the pole
        if mario.y <= self.flagpole_base_y:
            mario.y = self.flagpole_base_y
            game.world.mario.x = self.flagpole_x
            mario.facing_right = False

        # Check if Mario has reached the base
        if mario.y <= self.flagpole_base_y and not self._transition_started:
            # Transition to start level with screen fade
            from ..rendering import TransitionMode
            from .start_level import StartLevelState

            self._transition_started = True
            game.transition(StartLevelState(), TransitionMode.BOTH)
