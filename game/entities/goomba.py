"""Goomba enemy entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pygame import Rect, Surface

from ..camera import Camera
from ..constants import TILE_SIZE
from ..content import sprites
from ..physics.config import (
    GOOMBA_ANIMATION_FPS,
    GOOMBA_DEATH_DURATION,
    GOOMBA_GRAVITY,
    GOOMBA_GROUND_TOLERANCE,
    GOOMBA_SPEED,
    GOOMBA_STOMP_BOUNCE_VELOCITY,
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


class GoombaEntity(Entity):
    """Goomba enemy that walks horizontally and can be stomped."""

    def __init__(
        self,
        world_x: float,
        world_y: float,
        screen: int = 0,
        facing_right: bool = False,
    ):
        """Initialize Goomba.

        Args:
            world_x: X position in world pixels
            world_y: Y position in screen-relative pixels (0-224, from bottom)
            screen: Which vertical screen the entity is on
            facing_right: Initial facing direction (True=right)
        """
        super().__init__(world_x, world_y, screen)
        self.state.facing_right = facing_right
        self.configure_size(TILE_SIZE, TILE_SIZE)

        # Animation state
        self.animation_timer = 0.0
        self.animation_frame = 0

        # Death state
        self.is_dead = False
        self.death_timer = 0.0
        self.death_duration: float = float(GOOMBA_DEATH_DURATION)
        self.set_pipeline()

    def update(self, dt: float, level: Level) -> bool:
        """Update Goomba physics.

        Args:
            dt: Delta time in seconds
            level: Level for collision detection

        Returns:
            True to keep entity active, False to remove
        """
        if self.is_dead:
            self.death_timer += dt
            return self.death_timer < self.death_duration

        self.animation_timer += dt
        if self.animation_timer >= 1.0 / GOOMBA_ANIMATION_FPS:
            self.animation_timer = 0.0
            self.animation_frame = 1 - self.animation_frame

        self.process_pipeline(dt, level)

        return True

    def build_pipeline(self) -> Optional[EntityPipeline]:
        """Configure the reusable physics pipeline for Goomba movement."""
        return EntityPipeline(
            [
                GravityProcessor(gravity=GOOMBA_GRAVITY),
                HorizontalVelocityProcessor(speed=GOOMBA_SPEED),
                VelocityIntegrator(),
                WallBounceProcessor(speed=GOOMBA_SPEED),
                GroundSnapProcessor(tolerance=GOOMBA_GROUND_TOLERANCE),
            ]
        )

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the Goomba.

        Args:
            surface: Surface to draw on
            camera: Camera for coordinate transformation
        """
        screen_x, screen_y = camera.world_to_screen(self.state.x, self.state.y)

        if self.is_dead:
            # Draw squashed Goomba
            sprites.draw_at_position(
                surface,
                "enemies",
                "goomba_dead",
                int(screen_x),
                int(screen_y),
            )
        else:
            # Draw walking animation
            sprite_name = (
                "goomba_walk1" if self.animation_frame == 0 else "goomba_walk2"
            )
            sprites.draw_at_position(
                surface,
                "enemies",
                sprite_name,
                int(screen_x),
                int(screen_y),
            )

    def on_collide_mario(self, mario: "Mario") -> Optional[CollisionResponse]:
        """Handle collision with Mario.

        Args:
            mario: Mario's live object

        Returns:
            CollisionResponse describing what should happen
        """
        if self.is_dead:
            return None

        # Check if Mario is falling onto the Goomba (stomping)
        mario_bottom = mario.y
        goomba_top = self.state.y + self.state.height

        # Mario is stomping if falling and bottom is above top 1/3 of Goomba
        # This is more forgiving - allows stomping when hitting top portion
        stomp_threshold = goomba_top - (self.state.height * 0.33)  # Top third
        if mario.vy < 0 and mario_bottom > stomp_threshold:
            # Mario stomped the Goomba
            self.is_dead = True
            self.state.vx = 0  # Stop horizontal movement
            # Return response with bounce velocity for Mario
            return CollisionResponse(
                remove=False,
                bounce_velocity=GOOMBA_STOMP_BOUNCE_VELOCITY,
            )
        else:
            # Mario ran into the Goomba - damage Mario
            return CollisionResponse(damage=True)

    @property
    def is_stompable(self) -> bool:
        """Goombas can be stomped when they're alive.

        Returns:
            True if Goomba can be stomped, False if already dead
        """
        return not self.is_dead

    def get_collision_bounds(self) -> Rect:
        """Get collision rectangle for Goomba.

        Returns:
            Pygame Rect for collision detection
        """
        # Goomba sprite fits the tile perfectly, no margins needed
        return Rect(
            int(self.state.x),
            int(self.state.y),
            int(self.state.width),
            int(self.state.height),
        )

    @property
    def can_be_damaged_by_entities(self) -> bool:
        return not self.is_dead

    def on_collide_entity(self, source: Entity) -> bool:
        if not self.can_be_damaged_by_entities:
            return False
        self.is_dead = True
        return True
