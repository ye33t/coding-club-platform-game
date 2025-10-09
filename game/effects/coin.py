"""Coin effect that arcs upward and returns to the item box."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from pygame import Surface

from game.constants import SUB_TILE_SIZE
from game.content.types import SpriteKey

from ..camera import Camera
from .base import Effect

COIN_ANIM_1 = SpriteKey(sprite_sheet="coin", sprite_name="anim_1")
COIN_ANIM_2 = SpriteKey(sprite_sheet="coin", sprite_name="anim_2")
COIN_ANIM_3 = SpriteKey(sprite_sheet="coin", sprite_name="anim_3")
COIN_ANIM_4 = SpriteKey(sprite_sheet="coin", sprite_name="anim_4")

COIN_ANIM: list[SpriteKey] = [COIN_ANIM_1, COIN_ANIM_2, COIN_ANIM_3, COIN_ANIM_4]

FRAME_DURATION = 1.0 / 30.0  # Seconds per animation frame


@dataclass(frozen=True)
class _CoinPhysics:
    """Cached physics configuration for the coin effect."""

    jump_velocity: float
    gravity: float
    offset: float


@lru_cache(maxsize=1)
def _coin_physics() -> _CoinPhysics:
    """Load and cache coin physics values lazily to avoid circular imports."""

    from ..physics import config as physics_config

    return _CoinPhysics(
        jump_velocity=physics_config.COIN_JUMP_VELOCITY,
        gravity=physics_config.COIN_GRAVITY,
        offset=physics_config.COIN_OFFSET,
    )


def _coin_jump_velocity() -> float:
    return _coin_physics().jump_velocity


@dataclass(slots=True)
class CoinEffect(Effect):
    """Simple coin animation that jumps up then falls back down."""

    world_x: float
    world_y: float  # Bottom of the coin in world coordinates
    velocity_y: float = field(default_factory=_coin_jump_velocity)

    frame: int = 0
    frame_timer: float = 0.0
    _gravity: float = field(init=False, repr=False)
    _offset: float = field(init=False, repr=False)
    _start_y: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        physics = _coin_physics()
        self._gravity = physics.gravity
        self._offset = physics.offset
        self._start_y = self.world_y

    def update(self, dt: float) -> bool:
        """Advance the coin's position."""
        # Integrate velocity.
        self.world_y += self.velocity_y * dt
        self.velocity_y -= self._gravity * dt

        self.frame_timer += dt
        while self.frame_timer >= FRAME_DURATION:
            self.frame = (self.frame + 1) % len(COIN_ANIM)
            self.frame_timer -= FRAME_DURATION

        if self.velocity_y < 0 and self.world_y <= self._start_y + self._offset:
            return False
        return True

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the coin relative to the camera."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        from ..content import sprites

        sprites.draw_at_position(
            surface,
            COIN_ANIM[self.frame].sprite_sheet,
            COIN_ANIM[self.frame].sprite_name,
            int(screen_x) + SUB_TILE_SIZE // 2,
            int(screen_y),
        )
