"""Transient shard effect triggered when bricks are smashed."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import pygame
from pygame import Surface

from ..camera import Camera
from ..constants import NATIVE_HEIGHT, SUB_TILE_SIZE, TILE_SIZE
from ..content import sprites
from ..physics import config as physics_config
from .base import Effect

_SPRITE_SHEET = "block_shards"
_SHARD_SPRITES = ("brick_tl", "brick_tr", "brick_bl", "brick_br")


@dataclass(slots=True)
class _ShardState:
    """Physics state for an individual shard."""

    sprite_name: str
    center_x: float
    center_y: float
    velocity_x: float
    velocity_y: float
    angle_degrees: float
    angular_velocity: float


@dataclass(slots=True)
class SmashShardEffect(Effect):
    """Emit four brick shards that arc outwards then expire."""

    tile_world_x: float
    tile_world_y: float

    _shards: List[_ShardState] = field(init=False, default_factory=list)
    _elapsed: float = 0.0
    _lifetime: float = field(init=False)
    _gravity: float = field(init=False)
    _sprite_cache: Dict[str, Surface | None] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        horizontal_speed = physics_config.SMASH_SHARD_HORIZONTAL_VELOCITY
        top_vertical_speed = physics_config.SMASH_SHARD_TOP_VELOCITY_Y
        bottom_vertical_speed = physics_config.SMASH_SHARD_BOTTOM_VELOCITY_Y
        angular_speed = physics_config.SMASH_SHARD_ANGULAR_SPEED

        left_positions = (
            self.tile_world_x + SUB_TILE_SIZE / 2,
            self.tile_world_y + SUB_TILE_SIZE / 2,
        )
        right_positions = (
            self.tile_world_x + TILE_SIZE - SUB_TILE_SIZE / 2,
            self.tile_world_y + SUB_TILE_SIZE / 2,
        )
        top_y = self.tile_world_y + TILE_SIZE - SUB_TILE_SIZE / 2

        self._shards = [
            _ShardState(
                sprite_name="brick_tl",
                center_x=left_positions[0],
                center_y=top_y,
                velocity_x=-horizontal_speed,
                velocity_y=top_vertical_speed,
                angle_degrees=0.0,
                angular_velocity=-angular_speed,
            ),
            _ShardState(
                sprite_name="brick_tr",
                center_x=right_positions[0],
                center_y=top_y,
                velocity_x=horizontal_speed,
                velocity_y=top_vertical_speed,
                angle_degrees=0.0,
                angular_velocity=angular_speed,
            ),
            _ShardState(
                sprite_name="brick_bl",
                center_x=left_positions[0],
                center_y=left_positions[1],
                velocity_x=-horizontal_speed * 0.8,
                velocity_y=bottom_vertical_speed,
                angle_degrees=0.0,
                angular_velocity=-angular_speed * 0.75,
            ),
            _ShardState(
                sprite_name="brick_br",
                center_x=right_positions[0],
                center_y=right_positions[1],
                velocity_x=horizontal_speed * 0.8,
                velocity_y=bottom_vertical_speed,
                angle_degrees=0.0,
                angular_velocity=angular_speed * 0.75,
            ),
        ]

        self._gravity = physics_config.SMASH_SHARD_GRAVITY
        self._lifetime = physics_config.SMASH_SHARD_LIFETIME
        self._sprite_cache = {
            sprite: sprites.get_with_palette(_SPRITE_SHEET, sprite)
            for sprite in _SHARD_SPRITES
        }

    def update(self, dt: float) -> bool:  # noqa: D401
        """Move shards and return True while the effect is active."""
        self._elapsed += dt
        if self._elapsed >= self._lifetime:
            return False

        for shard in self._shards:
            shard.center_x += shard.velocity_x * dt
            shard.center_y += shard.velocity_y * dt
            shard.velocity_y -= self._gravity * dt
            shard.angle_degrees = (
                shard.angle_degrees + shard.angular_velocity * dt
            ) % 360.0

        return True

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render each shard with rotation relative to the camera."""
        for shard in self._shards:
            base_surface = self._sprite_cache.get(shard.sprite_name)
            if base_surface is None:
                continue

            rotated = pygame.transform.rotate(base_surface, shard.angle_degrees)
            screen_x, screen_y = camera.world_to_screen(
                shard.center_x, shard.center_y
            )
            draw_x = int(screen_x) - rotated.get_width() // 2
            draw_y = (
                int(NATIVE_HEIGHT - screen_y) - rotated.get_height() // 2
            )

            surface.blit(rotated, (draw_x, draw_y))
