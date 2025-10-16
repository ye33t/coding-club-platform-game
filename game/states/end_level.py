"""End-level sequence handling flag descent and castle celebration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from game.constants import TILE_SIZE

from ..effects import SpriteEffect
from ..physics.config import FLAGPOLE_DESCENT_SPEED, WALK_SPEED
from ..rendering import TransitionMode
from ..terrain.castle_exit import CastleExitBehavior
from ..terrain.flagpole import FlagpoleBehavior
from .base import State


class EndSequencePhase(Enum):
    """Phases for the end-of-level scripted sequence."""

    FLAG_DESCENT = auto()
    WALK_TO_CASTLE = auto()
    RAISE_CASTLE_FLAG = auto()
    COMPLETE = auto()


@dataclass
class CastleAnchors:
    """Data extracted from castle-related behaviors."""

    walk_target_x: Optional[float] = None
    flag_x: Optional[float] = None
    flag_final_y: Optional[float] = None
    flag_initial_y: Optional[float] = None


CASTLE_WALK_SPEED = WALK_SPEED * 0.6
CASTLE_FLAG_RAISE_SPEED = FLAGPOLE_DESCENT_SPEED
FLAG_SPRITE_WIDTH = TILE_SIZE


class EndLevelState(State):
    """State for Mario's post-flagpole celebration sequence."""

    def __init__(self, flagpole_x: float, flagpole_base_y: float):
        self.flagpole_x = flagpole_x
        self.flagpole_base_y = flagpole_base_y
        self.phase = EndSequencePhase.FLAG_DESCENT
        self._transition_started = False

        self._flag_effect: Optional[SpriteEffect] = None
        self._castle_flag_effect: Optional[SpriteEffect] = None

        self._flag_top_y: Optional[float] = None
        self._flag_current_y: Optional[float] = None
        self._flag_bottom_y: Optional[float] = None

        self._castle = CastleAnchors()

    def on_enter(self, game) -> None:
        """Initialize Mario position and supporting sprites."""
        mario = game.world.mario
        mario.x = self.flagpole_x - TILE_SIZE
        mario.vx = 0
        mario.facing_right = True
        mario.visible = True

        self._configure_flag(game)
        self._configure_castle(game)

    def on_exit(self, game) -> None:
        """Clean up effects created for the celebration sequence."""
        if self._flag_effect:
            self._flag_effect.deactivate()
        if self._castle_flag_effect:
            self._castle_flag_effect.deactivate()

    def update(self, game, dt: float) -> None:
        """Advance the celebration sequence frame-by-frame."""
        mario = game.world.mario

        # Keep the camera and transient effects in sync.
        game.world.camera.update(mario.x, game.world.level.width_pixels)
        game.world.effects.update(dt)

        self._update_flag_position(dt)

        if self.phase is EndSequencePhase.FLAG_DESCENT:
            self._update_flag_descent_phase(game, mario, dt)
        elif self.phase is EndSequencePhase.WALK_TO_CASTLE:
            self._update_walk_phase(game, mario, dt)
        elif self.phase is EndSequencePhase.RAISE_CASTLE_FLAG:
            self._update_castle_flag_phase(game, dt)

    # --- configuration helpers -------------------------------------------------

    def _configure_flag(self, game) -> None:
        """Spawn the flag sprite and cache pole bounds."""
        level = game.world.level
        flagpole_tiles = [
            instance
            for instance in level.terrain_manager.instances.values()
            if isinstance(instance.behavior, FlagpoleBehavior)
        ]

        if flagpole_tiles:
            max_tile_y = max(instance.y for instance in flagpole_tiles)
            self._flag_top_y = (max_tile_y + 1) * TILE_SIZE
        else:
            # Fallback to Mario's current top if flagpole metadata is missing.
            self._flag_top_y = game.world.mario.y + game.world.mario.height

        self._flag_bottom_y = self.flagpole_base_y + TILE_SIZE
        self._flag_current_y = self._flag_top_y

        flag_x = self.flagpole_x - FLAG_SPRITE_WIDTH
        self._flag_effect = SpriteEffect(
            sprite_sheet="other",
            sprite_name="flag",
            world_x=flag_x,
            world_y=self._flag_current_y,
            z_index=5,
        )
        game.world.effects.spawn(self._flag_effect)

    def _configure_castle(self, game) -> None:
        """Gather castle anchor data from terrain behaviors."""
        level = game.world.level
        mario = game.world.mario

        for instance in level.terrain_manager.instances.values():
            behavior = instance.behavior
            if not isinstance(behavior, CastleExitBehavior):
                continue

            if behavior.role == "walk":
                tile_left = behavior.world_x(instance.x)
                target_left = tile_left + (TILE_SIZE - mario.width) / 2
                self._castle.walk_target_x = target_left
            elif behavior.role == "flag":
                flag_x = behavior.world_x(instance.x)
                final_y = behavior.world_y(instance.y)
                initial_y = behavior.initial_flag_y(instance.y)
                self._castle.flag_x = flag_x
                self._castle.flag_final_y = final_y
                self._castle.flag_initial_y = initial_y

    # --- phase updates ---------------------------------------------------------

    def _update_flag_position(self, dt: float) -> None:
        if self._flag_current_y is None or self._flag_bottom_y is None:
            return

        self._flag_current_y = max(
            self._flag_bottom_y, self._flag_current_y - FLAGPOLE_DESCENT_SPEED * dt
        )

        if self._flag_effect:
            self._flag_effect.set_position(
                self._flag_effect.world_x, self._flag_current_y
            )

    def _update_flag_descent_phase(self, game, mario, dt: float) -> None:
        """Drive Mario down the flag and wait for both to reach the base."""
        mario.y -= FLAGPOLE_DESCENT_SPEED * dt

        if mario.y <= self.flagpole_base_y:
            mario.y = self.flagpole_base_y
            mario.x = self.flagpole_x
            mario.facing_right = False

        flag_reached_bottom = (
            self._flag_current_y is not None
            and self._flag_bottom_y is not None
            and self._flag_current_y <= self._flag_bottom_y + 0.1
        )

        if mario.y <= self.flagpole_base_y and flag_reached_bottom:
            self.phase = EndSequencePhase.WALK_TO_CASTLE
            mario.facing_right = True
            mario.action = "walking"

    def _update_walk_phase(self, game, mario, dt: float) -> None:
        """Script Mario's walk toward the castle entrance."""
        target_x = self._castle.walk_target_x
        if target_x is None:
            # No castle markers present; transition immediately.
            self._begin_completion(game)
            return

        mario.x += CASTLE_WALK_SPEED * dt
        if mario.x >= target_x:
            mario.x = target_x
            mario.vx = 0
            mario.action = "idle"
            mario.visible = False
            self._start_castle_flag(game)

    def _start_castle_flag(self, game) -> None:
        """Begin raising the castle flag once Mario is inside."""
        if self.phase is not EndSequencePhase.WALK_TO_CASTLE:
            return

        flag_x = self._castle.flag_x
        final_y = self._castle.flag_final_y
        initial_y = self._castle.flag_initial_y

        if flag_x is None or final_y is None or initial_y is None:
            self._begin_completion(game)
            return

        self._castle_flag_effect = SpriteEffect(
            sprite_sheet="other",
            sprite_name="flag_castle",
            world_x=flag_x,
            world_y=initial_y,
            z_index=5,
        )
        game.world.effects.spawn(self._castle_flag_effect)
        self.phase = EndSequencePhase.RAISE_CASTLE_FLAG

    def _update_castle_flag_phase(self, game, dt: float) -> None:
        """Animate the castle flag rising from the tower."""
        if not self._castle_flag_effect:
            self._begin_completion(game)
            return

        final_y = self._castle.flag_final_y
        if final_y is None:
            self._begin_completion(game)
            return

        current_y = min(
            final_y,
            self._castle_flag_effect.world_y + CASTLE_FLAG_RAISE_SPEED * dt,
        )
        self._castle_flag_effect.set_position(
            self._castle_flag_effect.world_x,
            current_y,
        )

        if current_y >= final_y - 0.1:
            self.phase = EndSequencePhase.COMPLETE
            self._begin_completion(game)

    # --- completion ------------------------------------------------------------

    def _begin_completion(self, game) -> None:
        """Trigger the fade-to-start transition once the sequence finishes."""
        if self._transition_started or game.transitioning:
            return

        from .start_level import StartLevelState

        self._transition_started = True
        game.transition(StartLevelState(), TransitionMode.BOTH)
