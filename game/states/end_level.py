"""End level state - Mario descending flagpole."""

from __future__ import annotations

from typing import Optional

from game.constants import TILE_SIZE

from ..physics.config import FLAGPOLE_DESCENT_SPEED
from ..props import FlagpoleProp
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
        self._flag_prop: Optional[FlagpoleProp] = None
        self._flag_descending = False
        self._flag_finished = False

    def on_enter(self, game) -> None:
        """Lock Mario to flagpole position."""
        # Lock Mario's X position to left of flagpole (offset by TILE_SIZE pixels)
        game.world.mario.x = self.flagpole_x - TILE_SIZE
        # Stop horizontal movement
        game.world.mario.vx = 0
        game.world.mario.facing_right = True

        prop = game.world.props.get("flagpole")
        if isinstance(prop, FlagpoleProp):
            self._flag_prop = prop
            self._flag_descending = True
            self._flag_finished = False
        else:
            self._flag_prop = None
            self._flag_descending = False
            self._flag_finished = True

    def update(self, game, dt: float) -> None:
        """Descend Mario down the flagpole."""
        mario = game.world.mario

        # Move Mario down at constant speed
        mario.y -= FLAGPOLE_DESCENT_SPEED * dt

        mario_at_base = False

        # Clamp Mario's position at the base and flip him to the other side of the pole
        if mario.y <= self.flagpole_base_y:
            mario.y = self.flagpole_base_y
            game.world.mario.x = self.flagpole_x
            mario.facing_right = False
            mario_at_base = True

        if self._flag_descending and not self._flag_finished:
            if self._flag_prop is not None:
                self._flag_finished = self._flag_prop.descend(dt)
            else:
                self._flag_finished = True

        # Check if Mario has reached the base
        if mario_at_base and self._flag_finished and not self._transition_started:
            if game.transitioning:
                return

            # Transition to start level with screen fade
            from ..rendering import TransitionMode
            from .start_level import StartLevelState

            self._transition_started = True
            game.transition(StartLevelState(), TransitionMode.BOTH)
