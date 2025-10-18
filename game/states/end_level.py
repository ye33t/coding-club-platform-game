"""End level sequence orchestrating Mario's flagpole finale."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pygame

from game.constants import NATIVE_WIDTH, TILE_SIZE

from ..mario import MarioIntent
from ..physics.config import FLAGPOLE_DESCENT_SPEED, WALK_SPEED
from ..props import FlagpoleProp
from ..terrain import CastleExitBehavior
from ..terrain.flagpole import FlagpoleBehavior
from .base import State
from .complete_level import CastleFlagAnchor, CastleWalkAnchor, CompleteLevelState


class SequencePhase(Enum):
    """High-level phases of the end-of-level sequence."""

    DESCENT = auto()
    CAMERA_EASE = auto()
    WALKING = auto()
    COMPLETE = auto()


@dataclass(frozen=True, slots=True)
class CastleAnchors:
    """Bundle of castle markers required for the finale."""

    walk: CastleWalkAnchor
    flag: CastleFlagAnchor | None


@dataclass(slots=True)
class CameraEaseState:
    """Tracks camera easing when centering on Mario."""

    duration: float
    active: bool = False
    elapsed: float = 0.0
    start_x: float = 0.0
    target_x: float = 0.0

    def reset(self, camera_x: float) -> None:
        """Reset to an idle state anchored at the current camera position."""
        self.active = False
        self.elapsed = 0.0
        self.start_x = camera_x
        self.target_x = camera_x

    def start(self, start_x: float, target_x: float) -> bool:
        """Begin easing toward the supplied camera target."""
        self.start_x = start_x
        self.target_x = target_x
        self.elapsed = 0.0

        if abs(target_x - start_x) <= 1e-2 or self.duration <= 0:
            self.active = False
            return False

        self.active = True
        return True

    def advance(self, game, dt: float) -> bool:
        """Advance the easing animation; returns True while still running."""
        if not self.active:
            return False

        self.elapsed = min(self.duration, self.elapsed + dt)
        t = 1.0 if self.duration <= 0 else min(1.0, self.elapsed / self.duration)

        camera = game.world.camera
        new_x = self.start_x + (self.target_x - self.start_x) * t
        camera.x = new_x
        if camera.max_x < new_x:
            camera.max_x = new_x

        if t >= 1.0:
            self.active = False
            return False

        return True


class EndLevelState(State):
    """Coordinates the flagpole descent, camera pan, and castle handoff.

    Phases:
    - DESCENT: Mario slides down while the decorative flag lowers.
    - CAMERA_EASE: The camera recenters before releasing Mario.
    - WALKING: Mario performs a scripted march into the castle archway.
    """

    CAMERA_EASE_DURATION = 0.75
    VICTORY_WALK_SPEED_SCALE = 0.6

    def __init__(self, flagpole_x: float, flagpole_base_y: float):
        """Initialize with flagpole geometry."""
        self.flagpole_x = flagpole_x
        self.flagpole_base_y = flagpole_base_y

        self._phase: SequencePhase = SequencePhase.DESCENT
        self._anchors: CastleAnchors | None = None
        self._flag_prop: FlagpoleProp | None = None
        self._flagpole_clamp_y: float | None = None
        self._camera_ease = CameraEaseState(duration=self.CAMERA_EASE_DURATION)
        self._transition_started = False
        self._victory_walk_speed = WALK_SPEED * self.VICTORY_WALK_SPEED_SCALE

    def on_enter(self, game) -> None:
        """Lock Mario to the pole and gather sequence metadata."""
        mario = game.world.mario
        mario.x = self.flagpole_x - TILE_SIZE
        mario.vx = 0.0
        mario.facing_right = True
        mario.set_intent_override(None)
        mario.visible = True

        self._phase = SequencePhase.DESCENT
        self._transition_started = False
        self._flag_prop = self._resolve_flag_prop(game)
        self._anchors = self._collect_castle_anchors(game)
        self._flagpole_clamp_y = self._determine_flagpole_clamp(game)
        self._camera_ease.reset(game.world.camera.x)
        self._apply_flagpole_top_clamp(mario)

    def update(self, game, dt: float) -> None:
        """Advance the current phase of the finale."""
        if self._phase is SequencePhase.DESCENT:
            if not self._run_flagpole_descent(game, dt):
                return
            if self._phase is SequencePhase.CAMERA_EASE:
                return

        if self._phase is SequencePhase.CAMERA_EASE:
            if self._camera_ease.advance(game, dt):
                return
            self._start_victory_walk(game, dt)
            return

        if self._phase is SequencePhase.WALKING:
            self._advance_victory_walk(game, dt)

    def on_exit(self, game) -> None:
        """Clear scripted intent and transient handles."""
        mario = game.world.mario
        mario.set_intent_override(None)
        mario.visible = True

        self._phase = SequencePhase.COMPLETE
        self._anchors = None
        self._flag_prop = None
        self._flagpole_clamp_y = None
        self._transition_started = False
        self._camera_ease.reset(game.world.camera.x)

    @staticmethod
    def _victory_walk_intent(_: pygame.key.ScancodeWrapper) -> MarioIntent:
        return MarioIntent(move_right=True)

    def _run_flagpole_descent(self, game, dt: float) -> bool:
        """Slide Mario down the pole while syncing the decorative flag."""
        mario = game.world.mario
        mario.y -= FLAGPOLE_DESCENT_SPEED * dt
        self._apply_flagpole_top_clamp(mario)

        if mario.y <= self.flagpole_base_y:
            mario.y = self.flagpole_base_y
            mario.x = self.flagpole_x - TILE_SIZE

        flag_prop = self._flag_prop
        if flag_prop is not None:
            was_complete = flag_prop.complete
            if not was_complete:
                flag_prop.descend(dt)
            if flag_prop.complete and not was_complete:
                self._handle_flag_drop_complete(game, dt)
        elif mario.y <= self.flagpole_base_y:
            self._handle_flag_drop_complete(game, dt)

        return self._phase is not SequencePhase.DESCENT

    def _handle_flag_drop_complete(self, game, dt: float) -> None:
        """Transition away from the descent once Mario reaches the base."""
        if self._phase is not SequencePhase.DESCENT:
            return

        mario = game.world.mario
        if mario.y > self.flagpole_base_y:
            return

        mario.facing_right = False
        mario.x = self.flagpole_x
        self._apply_flagpole_top_clamp(mario)

        if self._start_camera_center(game):
            self._phase = SequencePhase.CAMERA_EASE
        else:
            self._start_victory_walk(game, dt)

    def _start_camera_center(self, game) -> bool:
        """Start easing the camera toward Mario, returning True if animating."""
        camera = game.world.camera
        level_width = game.world.level.width_pixels
        mario = game.world.mario

        half_width = NATIVE_WIDTH / 2
        max_camera_x = max(0.0, level_width - NATIVE_WIDTH)
        target = max(0.0, min(mario.x - half_width, max_camera_x))
        target = max(camera.x, target)

        if self._camera_ease.start(camera.x, target):
            return True

        camera.x = target
        if camera.max_x < target:
            camera.max_x = target
        return False

    def _start_victory_walk(self, game, dt: float) -> None:
        """Kick off Mario's scripted march into the castle."""
        if self._phase is SequencePhase.WALKING:
            # Already walking, just advance.
            self._advance_victory_walk(game, dt)
            return

        mario = game.world.mario
        mario.vx = 0.0
        mario.facing_right = True
        game.world.camera.update(mario.x, game.world.level.width_pixels)
        mario.set_intent_override(self._victory_walk_intent)

        self._phase = SequencePhase.WALKING
        self._advance_victory_walk(game, dt)

    def _advance_victory_walk(self, game, dt: float) -> None:
        """Advance physics while constraining Mario's scripted speed."""
        mario = game.world.mario
        self._update_world(game, dt)
        self._cap_victory_speed(mario)
        self._check_castle_entry(game)

    def _check_castle_entry(self, game) -> None:
        """Hand off to the castle finale when Mario reaches the archway."""
        if self._transition_started or self._anchors is None:
            return

        mario = game.world.mario
        anchor = self._anchors.walk

        if mario.screen != anchor.screen:
            return

        trigger_x = anchor.world_x
        if mario.x < trigger_x:
            return

        mario.set_intent_override(None)
        mario.vx = 0.0
        mario.visible = False
        self._transition_started = True
        self._phase = SequencePhase.COMPLETE

        game.transition(CompleteLevelState(anchor, self._anchors.flag))

    def _update_world(self, game, dt: float) -> None:
        """Run a single physics tick with current scripted intent."""
        keys = pygame.key.get_pressed()
        game.world.update(keys, dt)

    def _cap_victory_speed(self, mario) -> None:
        """Clamp Mario's scripted walk speed for the victory march."""
        mario.vx = max(0.0, min(mario.vx, self._victory_walk_speed))

    def _collect_castle_anchors(self, game) -> CastleAnchors:
        """Collect required castle markers from terrain behaviors."""
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

        if walk_anchor is None:
            raise RuntimeError(
                "Missing castle_exit behavior with role 'walk'. "
                "Add a walk marker so the finale knows where to end."
            )

        if flag_anchor is None:
            print(  # noqa: T201 - best effort runtime warning
                "Warning: castle finale missing 'flag' castle_exit marker; "
                "flag raising animation will be skipped."
            )

        return CastleAnchors(walk=walk_anchor, flag=flag_anchor)

    def _determine_flagpole_clamp(self, game) -> float | None:
        """Determine the highest Y Mario should reach during descent."""
        flagpole_tiles = [
            instance
            for instance in game.world.level.terrain_manager.instances.values()
            if isinstance(instance.behavior, FlagpoleBehavior)
        ]

        if not flagpole_tiles:
            return None

        unique_rows = sorted({instance.y for instance in flagpole_tiles})
        if not unique_rows:
            return None

        clamp_tile_y = unique_rows[-2] if len(unique_rows) >= 2 else unique_rows[-1]
        return float(clamp_tile_y * TILE_SIZE)

    def _apply_flagpole_top_clamp(self, mario) -> None:
        """Prevent Mario from hovering above the pole's top tiles."""
        if self._flagpole_clamp_y is None:
            return
        if mario.y > self._flagpole_clamp_y:
            mario.y = self._flagpole_clamp_y

    def _resolve_flag_prop(self, game) -> FlagpoleProp | None:
        """Fetch the decorative flag prop if one was registered."""
        prop = game.world.props.get("flagpole")
        return prop if isinstance(prop, FlagpoleProp) else None
