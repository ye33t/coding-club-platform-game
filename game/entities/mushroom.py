"""Mushroom collectible entity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pygame import Surface

from ..camera import Camera
from ..constants import SUB_TILE_SIZE, TILE_SIZE
from ..content import sprites
from ..content.tile_definitions import is_quadrant_solid
from .base import CollisionResponse, Entity

if TYPE_CHECKING:
    from ..level import Level
    from ..mario import MarioState


MUSHROOM_SPEED = 50.0
MUSHROOM_GRAVITY = 400.0
GROUND_DETECTION_TOLERANCE = 2.0


class MushroomEntity(Entity):
    """Mushroom power-up collectible.

    Moves horizontally, bounces off walls, stays on platforms.
    """

    def __init__(
        self, world_x: float, world_y: float, screen: int = 0, direction: int = 1
    ):
        """Initialize mushroom.

        Args:
            world_x: X position in world pixels
            world_y: Y position in screen-relative pixels (0-224, from bottom)
            screen: Which vertical screen the entity is on
            direction: Initial horizontal direction (1=right, -1=left)
        """
        super().__init__(world_x, world_y, screen)
        self.state.direction = direction
        self.state.vx = MUSHROOM_SPEED * direction
        self.state.width = TILE_SIZE
        self.state.height = TILE_SIZE

    def update(self, dt: float, level: Level) -> bool:
        """Update mushroom physics.

        Args:
            dt: Delta time in seconds
            level: Level for collision detection

        Returns:
            True to keep entity active
        """
        self._apply_gravity(dt)
        self._apply_horizontal_movement(dt)
        self._check_wall_collision(level)
        self._check_ground_collision(level)

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
            int(screen_x) + SUB_TILE_SIZE // 2,
            int(screen_y),
        )

    def on_collide_mario(self, mario_state: MarioState) -> Optional[CollisionResponse]:
        """Handle collision with Mario.

        Args:
            mario_state: Mario's current state

        Returns:
            CollisionResponse to remove mushroom and apply power-up
        """
        return CollisionResponse(remove=True, power_up=True)

    def _apply_gravity(self, dt: float) -> None:
        """Apply gravity to mushroom velocity."""
        self.state.vy -= MUSHROOM_GRAVITY * dt

    def _apply_horizontal_movement(self, dt: float) -> None:
        """Update position based on velocity."""
        self.state.x += self.state.vx * dt
        self.state.y += self.state.vy * dt

    def _check_wall_collision(self, level: Level) -> None:
        """Check for wall collisions and reverse direction if hit.

        Args:
            level: Level for collision detection
        """
        if self.state.vx > 0:
            edge_x = self.state.x + self.state.width - 1
        else:
            edge_x = self.state.x

        sample_y = self.state.y + self.state.height / 2

        tile_x = int(edge_x // TILE_SIZE)
        tile_y = int(sample_y // TILE_SIZE)

        tile_type = level.get_terrain_tile(self.state.screen, tile_x, tile_y)
        tile_def = level.get_tile_definition(tile_type)

        if not tile_def or tile_def.collision_mask == 0:
            return

        x_in_tile = edge_x - (tile_x * TILE_SIZE)
        y_in_tile = sample_y - (tile_y * TILE_SIZE)

        quadrant_x = 0 if x_in_tile < (TILE_SIZE / 2) else 1
        quadrant_y = 0 if y_in_tile < (TILE_SIZE / 2) else 1

        if is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
            self.state.direction *= -1
            self.state.vx = MUSHROOM_SPEED * self.state.direction

            if self.state.direction > 0:
                self.state.x = (tile_x + 1) * TILE_SIZE
            else:
                self.state.x = (tile_x * TILE_SIZE) - self.state.width

    def _check_ground_collision(self, level: Level) -> None:
        """Check for ground collision and snap to surface.

        Args:
            level: Level for collision detection
        """
        highest_ground = -1.0
        found_ground = False

        sample_points = [
            self.state.x,
            self.state.x + self.state.width / 2,
            self.state.x + self.state.width - 1,
        ]

        for sample_x in sample_points:
            tile_x = int(sample_x // TILE_SIZE)
            base_tile_y = int(self.state.y // TILE_SIZE)

            for check_y in [base_tile_y, base_tile_y - 1]:
                if check_y < 0:
                    continue

                tile_type = level.get_terrain_tile(self.state.screen, tile_x, check_y)
                tile_def = level.get_tile_definition(tile_type)

                if not tile_def or tile_def.collision_mask == 0:
                    continue

                x_in_tile = sample_x - (tile_x * TILE_SIZE)
                quadrant_x = 0 if x_in_tile < (TILE_SIZE / 2) else 1

                for quadrant_y in [0, 1]:
                    if not is_quadrant_solid(tile_def, quadrant_x, quadrant_y):
                        continue

                    quadrant_top_y = check_y * TILE_SIZE + (quadrant_y + 1) * (
                        TILE_SIZE / 2
                    )

                    if (
                        abs(self.state.y - quadrant_top_y) <= GROUND_DETECTION_TOLERANCE
                        or self.state.y < quadrant_top_y
                    ):
                        if self.state.y <= quadrant_top_y + 1:
                            found_ground = True
                            if highest_ground < 0 or quadrant_top_y > highest_ground:
                                highest_ground = quadrant_top_y

        if found_ground and self.state.vy <= 0:
            self.state.y = highest_ground
            self.state.vy = 0
            self.state.on_ground = True
        else:
            self.state.on_ground = False
