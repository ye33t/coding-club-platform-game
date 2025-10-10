"""Goomba enemy entity."""

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


GOOMBA_SPEED = 30.0
GOOMBA_GRAVITY = 400.0
GROUND_DETECTION_TOLERANCE = 2.0
ANIMATION_SPEED = 4.0  # Frames per second
STOMP_BOUNCE_VELOCITY = 200.0  # Mario bounce velocity when stomping


class GoombaEntity(Entity):
    """Goomba enemy that walks horizontally and can be stomped."""

    def __init__(
        self, world_x: float, world_y: float, screen: int = 0, direction: int = -1
    ):
        """Initialize Goomba.

        Args:
            world_x: X position in world pixels
            world_y: Y position in screen-relative pixels (0-224, from bottom)
            screen: Which vertical screen the entity is on
            direction: Initial horizontal direction (1=right, -1=left)
        """
        super().__init__(world_x, world_y, screen)
        self.state.direction = direction
        self.state.vx = GOOMBA_SPEED * direction
        self.state.width = TILE_SIZE
        self.state.height = TILE_SIZE

        # Animation state
        self.animation_timer = 0.0
        self.animation_frame = 0

        # Death state
        self.is_dead = False
        self.death_timer = 0.0
        self.DEATH_DURATION = 0.5  # Time to show squashed sprite before removal

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
            return self.death_timer < self.DEATH_DURATION

        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= 1.0 / ANIMATION_SPEED:
            self.animation_timer = 0.0
            self.animation_frame = 1 - self.animation_frame

        # Apply physics
        self._apply_gravity(dt)
        self._apply_horizontal_movement(dt)
        self._check_wall_collision(level)
        self._check_ground_collision(level)

        return True

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
                int(screen_x) + SUB_TILE_SIZE // 2,
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
                int(screen_x) + SUB_TILE_SIZE // 2,
                int(screen_y),
            )

    def on_collide_mario(self, mario_state: MarioState) -> Optional[CollisionResponse]:
        """Handle collision with Mario.

        Args:
            mario_state: Mario's current state

        Returns:
            CollisionResponse describing what should happen
        """
        if self.is_dead:
            return None

        # Check if Mario is falling onto the Goomba (stomping)
        mario_bottom = mario_state.y
        goomba_top = self.state.y + self.state.height

        # Mario is stomping if falling and bottom is above Goomba's midpoint
        if mario_state.vy < 0 and mario_bottom > goomba_top - (self.state.height * 0.5):
            # Mario stomped the Goomba
            self.is_dead = True
            self.state.vx = 0  # Stop horizontal movement
            # Return response with bounce velocity for Mario
            return CollisionResponse(
                remove=False,  # Keep entity for death animation
                bounce_velocity=STOMP_BOUNCE_VELOCITY,
            )
        else:
            # Mario ran into the Goomba - damage Mario
            return CollisionResponse(damage=True)

    def _apply_gravity(self, dt: float) -> None:
        """Apply gravity to Goomba velocity."""
        self.state.vy -= GOOMBA_GRAVITY * dt

    def _apply_horizontal_movement(self, dt: float) -> None:
        """Update position based on velocity."""
        self.state.x += self.state.vx * dt
        self.state.y += self.state.vy * dt

    def _check_wall_collision(self, level: Level) -> None:
        """Check for wall collisions and reverse direction if hit.

        Args:
            level: Level for collision detection
        """
        # Determine which edge to check based on movement direction
        if self.state.vx > 0:
            edge_x = self.state.x + self.state.width - 1
        else:
            edge_x = self.state.x

        # Sample at mid-height
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
            # Bounce off wall
            self.state.direction *= -1
            self.state.vx = GOOMBA_SPEED * self.state.direction

            # Snap to tile edge
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

        # Sample points across the Goomba's width
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
