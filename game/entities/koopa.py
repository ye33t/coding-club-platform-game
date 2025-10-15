"""Koopa Troopa enemy and shell entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pygame import Surface

from ..camera import Camera
from ..constants import TILE_SIZE
from ..content import sprites
from ..physics.config import (
    KOOPA_SHELL_GRAVITY,
    KOOPA_SHELL_GROUND_TOLERANCE,
    KOOPA_SHELL_SPEED,
    KOOPA_SHELL_STOMP_BOUNCE_VELOCITY,
    KOOPA_TROOPA_ANIMATION_FPS,
    KOOPA_TROOPA_GRAVITY,
    KOOPA_TROOPA_GROUND_TOLERANCE,
    KOOPA_TROOPA_SPEED,
    KOOPA_TROOPA_STOMP_BOUNCE_VELOCITY,
)
from .base import CollisionResponse, Entity
from .physics import (
    EntityPipeline,
    GravityProcessor,
    GroundSnapProcessor,
    HorizontalVelocityProcessor,
    VelocityIntegrator,
    WallBounceProcessor,
)

if TYPE_CHECKING:
    from ..level import Level
    from ..mario import Mario


class KoopaTroopaEntity(Entity):
    """Koopa Troopa enemy that spawns a shell when stomped."""

    def __init__(
        self, world_x: float, world_y: float, screen: int = 0, direction: int = -1
    ):
        super().__init__(world_x, world_y, screen)
        self.state.direction = direction
        self.configure_size(TILE_SIZE, TILE_SIZE)

        self.animation_timer = 0.0
        self.animation_frame = 0
        self._stomped = False

        self.set_pipeline()

    def update(self, dt: float, level: Level) -> bool:
        """Advance Koopa physics and animation."""
        if not self._stomped:
            self.animation_timer += dt
            if self.animation_timer >= 1.0 / KOOPA_TROOPA_ANIMATION_FPS:
                self.animation_timer = 0.0
                self.animation_frame = 1 - self.animation_frame

            self.process_pipeline(dt, level)

        return True

    def build_pipeline(self) -> Optional[EntityPipeline]:
        """Configure the Koopa Troopa physics pipeline."""
        return EntityPipeline(
            [
                GravityProcessor(gravity=KOOPA_TROOPA_GRAVITY),
                HorizontalVelocityProcessor(speed=KOOPA_TROOPA_SPEED),
                VelocityIntegrator(),
                WallBounceProcessor(speed=KOOPA_TROOPA_SPEED),
                GroundSnapProcessor(tolerance=KOOPA_TROOPA_GROUND_TOLERANCE),
            ]
        )

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the Koopa Troopa."""
        if self._stomped:
            return

        screen_x, screen_y = camera.world_to_screen(self.state.x, self.state.y)
        sprite_name = (
            "koopa_troopa_walk1" if self.animation_frame == 0 else "koopa_troopa_walk2"
        )
        sprites.draw_at_position(
            surface,
            "enemies",
            sprite_name,
            int(screen_x),
            int(screen_y),
            reflected=self.state.direction < 0,
        )

    def on_collide_mario(self, mario: "Mario") -> Optional[CollisionResponse]:
        """Handle Mario collision, spawning a shell on stomp."""
        if self._stomped:
            return None

        mario_bottom = mario.y
        koopa_top = self.state.y + self.state.height
        stomp_threshold = koopa_top - (self.state.height * 0.33)

        if mario.vy < 0 and mario_bottom > stomp_threshold:
            self._stomped = True
            self.state.direction = 0

            shell = ShellEntity(
                world_x=self.state.x,
                world_y=self.state.y,
                screen=self.state.screen,
                direction=-1 if mario.facing_right else 1,
            )

            return CollisionResponse(
                remove=True,
                bounce_velocity=KOOPA_TROOPA_STOMP_BOUNCE_VELOCITY,
                spawn_entity=shell,
            )

        return CollisionResponse(damage=True)

    @property
    def is_stompable(self) -> bool:
        return not self._stomped


class ShellEntity(Entity):
    """Stationary Koopa shell spawned after stomping a Koopa Troopa."""

    def __init__(
        self, world_x: float, world_y: float, screen: int = 0, direction: int = 0
    ):
        super().__init__(world_x, world_y, screen)
        self.state.direction = direction
        self.configure_size(TILE_SIZE, TILE_SIZE)
        self.set_pipeline()

    def update(self, dt: float, level: Level) -> bool:
        """Apply gravity to keep the shell grounded."""
        self.process_pipeline(dt, level)
        return True

    def build_pipeline(self) -> Optional[EntityPipeline]:
        """Configure shell physics."""
        return EntityPipeline(
            [
                GravityProcessor(gravity=KOOPA_SHELL_GRAVITY),
                HorizontalVelocityProcessor(speed=KOOPA_SHELL_SPEED),
                VelocityIntegrator(),
                GroundSnapProcessor(tolerance=KOOPA_SHELL_GROUND_TOLERANCE),
            ]
        )

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the Koopa shell."""
        screen_x, screen_y = camera.world_to_screen(self.state.x, self.state.y)
        sprites.draw_at_position(
            surface,
            "enemies",
            "koopa_troopa_shell",
            int(screen_x),
            int(screen_y),
        )

    def on_collide_mario(self, mario: "Mario") -> Optional[CollisionResponse]:
        """Bounce Mario when stomping; damage otherwise."""
        mario_bottom = mario.y
        shell_top = self.state.y + self.state.height
        stomp_threshold = shell_top - (self.state.height * 0.33)

        if mario.vy < 0 and mario_bottom > stomp_threshold:
            return CollisionResponse(
                remove=False,
                bounce_velocity=KOOPA_SHELL_STOMP_BOUNCE_VELOCITY,
            )

        return CollisionResponse(damage=True)

    @property
    def is_stompable(self) -> bool:
        return True
