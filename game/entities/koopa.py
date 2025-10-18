"""Koopa Troopa enemy and shell entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
from pygame import Rect, Surface

from ..camera import Camera
from ..constants import NATIVE_HEIGHT, TILE_SIZE
from ..content import sprites
from ..physics.config import (
    ENTITY_KNOCKOUT_VELOCITY_X,
    ENTITY_KNOCKOUT_VELOCITY_Y,
    KOOPA_SHELL_GRAVITY,
    KOOPA_SHELL_GROUND_TOLERANCE,
    KOOPA_SHELL_KICK_SPEED,
    KOOPA_SHELL_SPEED,
    KOOPA_SHELL_STOMP_BOUNCE_VELOCITY,
    KOOPA_TROOPA_ANIMATION_FPS,
    KOOPA_TROOPA_GRAVITY,
    KOOPA_TROOPA_GROUND_TOLERANCE,
    KOOPA_TROOPA_SPEED,
    KOOPA_TROOPA_STOMP_BOUNCE_VELOCITY,
)
from .base import CollisionResponse, Entity
from .mixins import (
    HorizontalMovementConfig,
    HorizontalMovementMixin,
    KnockoutMixin,
    KnockoutSettings,
)

if TYPE_CHECKING:
    from ..level import Level
    from ..mario import Mario


class KoopaTroopaEntity(HorizontalMovementMixin, KnockoutMixin, Entity):
    """Koopa Troopa enemy that spawns a shell when stomped."""

    def __init__(
        self,
        world_x: float,
        world_y: float,
        screen: int = 0,
        facing_right: bool = False,
    ):
        super().__init__(world_x, world_y, screen)
        self.state.facing_right = facing_right
        self.configure_size(TILE_SIZE, TILE_SIZE)

        self.animation_timer = 0.0
        self.animation_frame = 0
        self._stomped = False

        self.init_horizontal_movement(
            HorizontalMovementConfig(
                gravity=KOOPA_TROOPA_GRAVITY,
                speed=KOOPA_TROOPA_SPEED,
                ground_snap_tolerance=KOOPA_TROOPA_GROUND_TOLERANCE,
            )
        )
        self.init_knockout(
            KnockoutSettings(
                vertical_velocity=ENTITY_KNOCKOUT_VELOCITY_Y,
                horizontal_velocity=ENTITY_KNOCKOUT_VELOCITY_X,
                gravity=KOOPA_TROOPA_GRAVITY,
            )
        )

        self.set_pipeline()

    def update(self, dt: float, level: Level) -> bool:
        """Advance Koopa physics and animation."""
        knockout_result = self.update_knockout(dt)
        if knockout_result is not None:
            return knockout_result

        if not self._stomped:
            self.animation_timer += dt
            if self.animation_timer >= 1.0 / KOOPA_TROOPA_ANIMATION_FPS:
                self.animation_timer = 0.0
                self.animation_frame = 1 - self.animation_frame

            self.process_pipeline(dt, level)

        return True

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the Koopa Troopa."""
        if self._stomped and not self.knocked_out:
            return

        screen_x, screen_y = camera.world_to_screen(self.state.x, self.state.y)
        sprite_name = (
            "koopa_troopa_walk1" if self.animation_frame == 0 else "koopa_troopa_walk2"
        )
        if self.knocked_out:
            sprite = sprites.get("koopas", sprite_name)
            if sprite is None:
                return
            flipped = pygame.transform.flip(sprite, False, True)
            draw_x = int(screen_x)
            screen_y_px = NATIVE_HEIGHT - int(screen_y)
            draw_y = screen_y_px - flipped.get_height()
            surface.blit(flipped, (draw_x, draw_y))
        else:
            sprites.draw_at_position(
                surface,
                "koopas",
                sprite_name,
                int(screen_x),
                int(screen_y),
                reflected=self.state.facing_right,
            )

    @property
    def can_be_damaged_by_entities(self) -> bool:
        return not self._stomped

    def on_collide_entity(self, source: Entity) -> bool:
        if self.knocked_out:
            return False

        if source.can_damage_entities and self.can_be_damaged_by_entities:
            self.trigger_knockout(source)
            return False

        if source.blocks_entities and not self._stomped:
            self.handle_blocking_entity(source)

        return False

    def on_collide_mario(self, mario: "Mario") -> Optional[CollisionResponse]:
        """Handle Mario collision, spawning a shell on stomp."""
        if self._stomped or self.knocked_out:
            return None

        mario_bottom = mario.y
        koopa_top = self.state.y + self.state.height
        stomp_threshold = koopa_top - (self.state.height * 0.33)

        if mario.vy < 0 and mario_bottom > stomp_threshold:
            self._stomped = True
            self.state.vx = 0.0
            self.state.facing_right = False

            shell = ShellEntity(
                world_x=self.state.x,
                world_y=self.state.y,
                screen=self.state.screen,
                facing_right=not mario.facing_right,
            )

            return CollisionResponse(
                remove=True,
                bounce_velocity=KOOPA_TROOPA_STOMP_BOUNCE_VELOCITY,
                spawn_entity=shell,
            )

        return CollisionResponse(damage=True)

    @property
    def is_stompable(self) -> bool:
        return not self._stomped and not self.knocked_out

    def on_knockout(self, source: Entity) -> None:
        self._stomped = False


class ShellEntity(HorizontalMovementMixin, KnockoutMixin, Entity):
    """Koopa shell that toggles between stationary and moving states."""

    SHELL_KICK_COOLDOWN = 0.1

    def __init__(
        self,
        world_x: float,
        world_y: float,
        screen: int = 0,
        facing_right: bool = False,
    ):
        super().__init__(world_x, world_y, screen)
        self.state.facing_right = facing_right
        self.configure_size(TILE_SIZE, TILE_SIZE)
        self.kick_cooldown = 0.0

        self.init_horizontal_movement(
            HorizontalMovementConfig(
                gravity=KOOPA_SHELL_GRAVITY,
                speed=KOOPA_SHELL_SPEED,
                ground_snap_tolerance=KOOPA_SHELL_GROUND_TOLERANCE,
            )
        )
        self.init_knockout(
            KnockoutSettings(
                vertical_velocity=ENTITY_KNOCKOUT_VELOCITY_Y,
                horizontal_velocity=ENTITY_KNOCKOUT_VELOCITY_X,
                gravity=KOOPA_SHELL_GRAVITY,
            )
        )
        self.set_pipeline()

    @property
    def can_damage_entities(self) -> bool:
        return self.is_moving and self.kick_cooldown <= 0.0 and not self.knocked_out

    @property
    def can_be_damaged_by_entities(self) -> bool:
        return not self.knocked_out

    @property
    def blocks_entities(self) -> bool:
        return not self.is_moving and not self.knocked_out

    def update(self, dt: float, level: Level) -> bool:
        """Apply gravity and movement based on current state."""
        knockout_result = self.update_knockout(dt)
        if knockout_result is not None:
            return knockout_result

        if self.kick_cooldown > 0.0:
            self.kick_cooldown = max(0.0, self.kick_cooldown - dt)

        self.process_pipeline(dt, level)
        return True

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the Koopa shell."""
        screen_x, screen_y = camera.world_to_screen(self.state.x, self.state.y)
        if self.knocked_out:
            sprite = sprites.get("koopas", "koopa_troopa_shell")
            if sprite is None:
                return
            flipped = pygame.transform.flip(sprite, False, True)
            draw_x = int(screen_x)
            screen_y_px = NATIVE_HEIGHT - int(screen_y)
            draw_y = screen_y_px - flipped.get_height()
            surface.blit(flipped, (draw_x, draw_y))
        else:
            sprites.draw_at_position(
                surface,
                "koopas",
                "koopa_troopa_shell",
                int(screen_x),
                int(screen_y),
            )

    def on_collide_mario(self, mario: "Mario") -> Optional[CollisionResponse]:
        """Toggle movement based on stomp direction."""
        mario_bottom = mario.y
        shell_top = self.state.y + self.state.height
        stomp_threshold = shell_top - (self.state.height * 0.33)
        is_stomp = mario.vy < 0 and mario_bottom > stomp_threshold

        if not is_stomp:
            if self.is_moving:
                if self.kick_cooldown > 0.0:
                    return None
                return CollisionResponse(damage=True)

            self._set_moving(True, facing_right=mario.facing_right)
            self.kick_cooldown = self.SHELL_KICK_COOLDOWN
            return None

        facing_right = mario.facing_right

        if self.is_moving:
            self._set_moving(False)
        else:
            self._set_moving(True, facing_right=facing_right)
            self.kick_cooldown = self.SHELL_KICK_COOLDOWN

        return CollisionResponse(
            remove=False,
            bounce_velocity=KOOPA_SHELL_STOMP_BOUNCE_VELOCITY,
        )

    def on_collide_entity(self, source: Entity) -> bool:
        if self.knocked_out:
            return False

        if isinstance(source, ShellEntity):
            if source.knocked_out:
                return False

            if source.is_moving and self.is_moving:
                self.trigger_knockout(source)
                source.trigger_knockout(self)
                return False

            if source.is_moving and not self.is_moving:
                self.trigger_knockout(source)
                return False

            if not source.is_moving and self.is_moving:
                if not source.knocked_out:
                    source.trigger_knockout(self)
                return False

            return False

        if source.can_damage_entities and self.can_be_damaged_by_entities:
            self.trigger_knockout(source)
            return False

        return False

    def kick(self, facing_right: bool) -> None:
        """Start the shell moving in the provided direction."""
        self._set_moving(True, facing_right=facing_right)
        self.kick_cooldown = self.SHELL_KICK_COOLDOWN

    def stop(self) -> None:
        """Stop the shell in place."""
        self._set_moving(False)

    @property
    def is_stompable(self) -> bool:
        return True

    @property
    def is_moving(self) -> bool:
        return self._horizontal_processor.speed != 0.0

    def _set_moving(self, moving: bool, *, facing_right: Optional[bool] = None) -> None:
        if facing_right is not None:
            self.state.facing_right = facing_right

        speed = KOOPA_SHELL_KICK_SPEED if moving else KOOPA_SHELL_SPEED
        self._horizontal_processor.speed = speed
        self._wall_bounce_processor.speed = speed
        self.state.vx = speed if self.state.facing_right else -speed
        if not moving:
            self.state.vx = 0.0
            self.kick_cooldown = 0.0

    def on_knockout(self, source: Entity) -> None:
        self._horizontal_processor.speed = 0.0
        self._wall_bounce_processor.speed = 0.0

    def _determine_contact_side(self, mario: "Mario") -> str:
        """Determine which side of the shell Mario contacted."""
        shell_rect: Rect = self.get_collision_bounds()
        shell_center = shell_rect.centerx

        tolerance = 1.0
        front_edge = mario.x + mario.width if mario.facing_right else mario.x
        back_edge = mario.x if mario.facing_right else mario.x + mario.width

        def classify(edge_x: float) -> Optional[str]:
            if shell_rect.left - tolerance <= edge_x <= shell_rect.right + tolerance:
                return "left" if edge_x <= shell_center else "right"
            return None

        front_side = classify(front_edge)
        if front_side is not None:
            return front_side

        back_side = classify(back_edge)
        if back_side is not None:
            return back_side

        mario_center = mario.x + (mario.width / 2)
        return "left" if mario_center <= shell_center else "right"
