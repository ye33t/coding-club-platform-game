"""Mushroom collectible entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pygame import Surface

from ..camera import Camera
from ..constants import TILE_SIZE
from ..content import sprites
from ..physics.config import (
    MUSHROOM_EMERGE_SPEED,
    MUSHROOM_GRAVITY,
    MUSHROOM_GROUND_TOLERANCE,
    MUSHROOM_SPEED,
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


class MushroomEntity(Entity):
    """Mushroom power-up collectible.

    Moves horizontally, bounces off walls, stays on platforms.
    """

    def __init__(
        self,
        world_x: float,
        world_y: float,
        screen: int,
        facing_right: bool,
    ):
        """Initialize mushroom.

        Args:
            world_x: X position in world pixels
            world_y: Y position in screen-relative pixels (0-224, from bottom)
            screen: Which vertical screen the entity is on
            facing_right: Initial facing direction (True=right)
        """
        super().__init__(world_x, world_y, screen)
        self.state.facing_right = facing_right
        self.configure_size(TILE_SIZE, TILE_SIZE)

        self.emerging = True
        self.emerge_target_y = world_y + TILE_SIZE
        self.z_index = -10
        self.final_facing_right = facing_right
        self.set_pipeline()

    def update(self, dt: float, level: Level) -> bool:
        """Update mushroom physics.

        Args:
            dt: Delta time in seconds
            level: Level for collision detection

        Returns:
            True to keep entity active
        """
        if self.emerging:
            self.state.y += MUSHROOM_EMERGE_SPEED * dt

            if self.state.y >= self.emerge_target_y:
                self.state.y = self.emerge_target_y
                self.emerging = False
                self.z_index = 10
                self.state.facing_right = self.final_facing_right
        else:
            self.process_pipeline(dt, level)

        return True

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the mushroom.

        Args:
            surface: Surface to draw on
            camera: Camera for coordinate transformation
        """
        screen_x, screen_y = camera.world_to_screen(self.state.x, self.state.y)

        sprites.draw_at_position(
            surface,
            "other",
            "mushroom",
            int(screen_x),
            int(screen_y),
        )

    def on_collide_mario(self, mario: "Mario") -> Optional[CollisionResponse]:
        """Handle collision with Mario.

        Args:
            mario: Mario's live object

        Returns:
            CollisionResponse to remove mushroom and apply power-up
        """
        return CollisionResponse(
            remove=True,
            power_up_type="mushroom",
        )

    def build_pipeline(self) -> Optional[EntityPipeline]:
        """Configure physics for post-emerge mushroom behavior."""
        return EntityPipeline(
            [
                GravityProcessor(gravity=MUSHROOM_GRAVITY),
                HorizontalVelocityProcessor(speed=MUSHROOM_SPEED),
                VelocityIntegrator(),
                WallBounceProcessor(speed=MUSHROOM_SPEED),
                GroundSnapProcessor(tolerance=MUSHROOM_GROUND_TOLERANCE),
            ]
        )

    @property
    def can_be_damaged_by_entities(self) -> bool:
        return True

    def on_collide_entity(self, source: Entity) -> bool:
        return True
