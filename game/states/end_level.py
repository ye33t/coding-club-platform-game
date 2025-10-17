"""End level state - Mario descending flagpole."""

from __future__ import annotations

from typing import Optional

import pygame

from game.constants import SUB_TILE_SIZE, TILE_SIZE

from ..mario import MarioIntent
from ..physics.config import FLAGPOLE_DESCENT_SPEED
from ..props import FlagpoleProp
from ..terrain import CastleExitBehavior
from .base import State
from .complete_level import CastleFlagAnchor, CastleWalkAnchor, CompleteLevelState


class EndLevelState(State):
    """State for Mario descending the flagpole.

    This state:
    - Locks Mario's X position to the flagpole center
    - Descends Mario at constant speed
    - Starts Mario toward the castle entrance
    - Hands off to CompleteLevelState once Mario reaches the archway
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

        self._walk_started = False
        self._castle_walk_anchor: CastleWalkAnchor | None = None
        self._castle_flag_anchor: CastleFlagAnchor | None = None

    def on_enter(self, game) -> None:
        """Lock Mario to flagpole position."""
        # Lock Mario's X position to left of flagpole (offset by TILE_SIZE pixels)
        mario = game.world.mario
        mario.x = self.flagpole_x - TILE_SIZE
        # Stop horizontal movement
        mario.vx = 0
        mario.facing_right = True
        self._walk_started = False

        prop = game.world.props.get("flagpole")
        if isinstance(prop, FlagpoleProp):
            self._flag_prop = prop
        else:
            self._flag_prop = None

        self._collect_castle_anchors(game)

    def update(self, game, dt: float) -> None:
        """Descend Mario down the flagpole."""
        mario = game.world.mario

        if self._walk_started:
            game.world.update(pygame.key.get_pressed(), dt)
            self._check_castle_entry(game)
            return

        # Move Mario down at constant speed
        mario.y -= FLAGPOLE_DESCENT_SPEED * dt

        # Clamp Mario's position at the base and flip him to the other side of the pole
        if mario.y <= self.flagpole_base_y:
            mario.y = self.flagpole_base_y
            mario.x = self.flagpole_x
            mario.facing_right = False

        at_base = mario.y <= self.flagpole_base_y

        if self._flag_prop is not None and not self._flag_prop.complete:
            self._flag_prop.descend(dt)
            return

        if at_base and not self._walk_started:
            self._begin_walk(game)
            game.world.update(pygame.key.get_pressed(), dt)
            return

    def on_exit(self, game) -> None:
        mario = game.world.mario
        mario.set_intent_override(None)
        self._walk_started = False
        self._flag_prop = None
        self._castle_walk_anchor = None
        self._castle_flag_anchor = None

    def _begin_walk(self, game) -> None:
        if self._walk_started:
            return

        def _walk_intent(_: pygame.key.ScancodeWrapper) -> MarioIntent:
            return MarioIntent(move_right=True)

        game.world.mario.set_intent_override(_walk_intent)
        self._walk_started = True

    def _collect_castle_anchors(self, game) -> None:
        walk_anchor: CastleWalkAnchor | None = None
        flag_anchor: CastleFlagAnchor | None = None

        for instance in game.world.level.terrain_manager.instances.values():
            behavior = instance.behavior
            if not isinstance(behavior, CastleExitBehavior):
                continue

            world_x = behavior.world_x(instance.x)
            world_y = behavior.world_y(instance.y)

            if behavior.role == "walk" and walk_anchor is None:
                walk_anchor = CastleWalkAnchor(
                    screen=instance.screen,
                    world_x=world_x,
                    world_y=world_y,
                )
            elif behavior.role == "flag" and flag_anchor is None:
                flag_anchor = CastleFlagAnchor(
                    screen=instance.screen,
                    world_x=world_x,
                    final_y=world_y,
                    initial_y=behavior.initial_flag_y(instance.y),
                )

            if walk_anchor and flag_anchor:
                break

        self._castle_walk_anchor = walk_anchor
        self._castle_flag_anchor = flag_anchor

        if self._castle_walk_anchor is None:
            raise RuntimeError(
                "EndLevelState requires a castle exit marker with role 'walk'. "
                "Add a `castle_exit` behavior with `role: walk` to the level."
            )

        if self._castle_flag_anchor is None:
            raise RuntimeError(
                "EndLevelState requires a castle exit marker with role 'flag'. "
                "Add a `castle_exit` behavior with `role: flag` to the level."
            )

    def _check_castle_entry(self, game) -> None:
        if self._transition_started or self._castle_walk_anchor is None:
            return

        mario = game.world.mario
        anchor = self._castle_walk_anchor

        if mario.screen != anchor.screen:
            return

        trigger_x = anchor.world_x + SUB_TILE_SIZE // 2
        if mario.x < trigger_x:
            return

        mario.set_intent_override(None)
        mario.vx = 0.0
        mario.visible = False
        self._transition_started = True

        game.transition(
            CompleteLevelState(self._castle_walk_anchor, self._castle_flag_anchor)
        )
