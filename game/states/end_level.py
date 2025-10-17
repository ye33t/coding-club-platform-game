"""End level state - Mario descending flagpole."""

from __future__ import annotations

from typing import Optional

import pygame

from game.constants import NATIVE_WIDTH, TILE_SIZE

from ..mario import MarioIntent
from ..physics.config import FLAGPOLE_DESCENT_SPEED, WALK_SPEED
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
        self._victory_walk_speed = WALK_SPEED * 0.6
        self._flag_drop_complete = False
        self._camera_center_active = False
        self._camera_center_elapsed = 0.0
        self._camera_center_duration = 0.75
        self._camera_start_x = 0.0
        self._camera_target_x = 0.0

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
        self._flag_drop_complete = False
        self._camera_center_active = False
        self._camera_center_elapsed = 0.0
        camera = game.world.camera
        self._camera_start_x = camera.x
        self._camera_target_x = camera.x

    def update(self, game, dt: float) -> None:
        """Advance end-of-level sequence."""
        mario = game.world.mario

        if not self._flag_drop_complete:
            self._update_flagpole_descent(game, mario, dt)
            if not self._flag_drop_complete:
                return

        if self._camera_center_active:
            self._update_camera_center(game, dt)
            if self._camera_center_active:
                return

        if not self._walk_started:
            self._begin_walk(game)
            game.world.update(pygame.key.get_pressed(), dt)
            self._cap_victory_speed(mario)
            return

        game.world.update(pygame.key.get_pressed(), dt)
        self._cap_victory_speed(mario)
        self._check_castle_entry(game)

    def on_exit(self, game) -> None:
        mario = game.world.mario
        mario.set_intent_override(None)
        self._walk_started = False
        self._flag_prop = None
        self._castle_walk_anchor = None
        self._castle_flag_anchor = None
        self._flag_drop_complete = False
        self._camera_center_active = False
        self._camera_center_elapsed = 0.0

    def _begin_walk(self, game) -> None:
        if self._walk_started:
            return

        def _walk_intent(_: pygame.key.ScancodeWrapper) -> MarioIntent:
            return MarioIntent(move_right=True)

        mario = game.world.mario
        mario.vx = 0.0
        mario.facing_right = True
        game.world.camera.update(mario.x, game.world.level.width_pixels)
        mario.set_intent_override(_walk_intent)
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

        trigger_x = anchor.world_x + TILE_SIZE * 0.5
        if mario.x < trigger_x:
            return

        mario.set_intent_override(None)
        mario.vx = 0.0
        mario.visible = False
        self._transition_started = True

        game.transition(
            CompleteLevelState(self._castle_walk_anchor, self._castle_flag_anchor)
        )

    def _update_flagpole_descent(self, game, mario, dt: float) -> None:
        """Slide Mario down the pole while the flag falls."""
        mario.y -= FLAGPOLE_DESCENT_SPEED * dt
        if mario.y <= self.flagpole_base_y:
            mario.y = self.flagpole_base_y
            mario.x = self.flagpole_x - TILE_SIZE

        flag_prop = self._flag_prop
        if flag_prop is not None:
            was_complete = flag_prop.complete
            if not was_complete:
                flag_prop.descend(dt)
            if flag_prop.complete and not was_complete:
                self._on_flag_drop_complete(game)
        elif mario.y <= self.flagpole_base_y:
            self._on_flag_drop_complete(game)

    def _on_flag_drop_complete(self, game) -> None:
        """Trigger the pause once both Mario and the flag reach the base."""
        if self._flag_drop_complete:
            return

        mario = game.world.mario
        if mario.y > self.flagpole_base_y:
            return

        mario.facing_right = False
        mario.x = self.flagpole_x
        self._flag_drop_complete = True
        self._start_camera_center(game)

    def _start_camera_center(self, game) -> None:
        """Begin easing the camera to keep Mario centered."""
        camera = game.world.camera
        level_width = game.world.level.width_pixels
        mario = game.world.mario

        half_width = NATIVE_WIDTH / 2
        max_camera_x = max(0.0, level_width - NATIVE_WIDTH)
        target = max(0.0, min(mario.x - half_width, max_camera_x))
        target = max(camera.x, target)

        self._camera_start_x = camera.x
        self._camera_target_x = target
        self._camera_center_elapsed = 0.0

        if abs(target - camera.x) <= 1e-2 or self._camera_center_duration <= 0:
            camera.x = target
            if camera.max_x < target:
                camera.max_x = target
            self._camera_center_active = False
        else:
            self._camera_center_active = True

    def _update_camera_center(self, game, dt: float) -> None:
        """Ease the camera toward its target center position."""
        if not self._camera_center_active:
            return

        self._camera_center_elapsed = min(
            self._camera_center_elapsed + dt, self._camera_center_duration
        )

        if self._camera_center_duration <= 0:
            t = 1.0
        else:
            t = min(1.0, self._camera_center_elapsed / self._camera_center_duration)

        new_x = (
            self._camera_start_x + (self._camera_target_x - self._camera_start_x) * t
        )

        camera = game.world.camera
        camera.x = new_x
        if camera.max_x < new_x:
            camera.max_x = new_x

        if t >= 1.0:
            self._camera_center_active = False

    def _cap_victory_speed(self, mario) -> None:
        """Clamp Mario's scripted walk speed for the victory march."""
        mario.vx = max(0.0, min(mario.vx, self._victory_walk_speed))
