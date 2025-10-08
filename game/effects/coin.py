"""Coin effect that arcs upward and returns to the item box."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from pygame import Surface

from ..camera import Camera
from .base import Effect

# Tunable physics constants for the coin arc.
COIN_JUMP_VELOCITY = 200.0  # pixels per second
COIN_GRAVITY = 600.0  # pixels per second squared


@dataclass
class CoinEffect(Effect):
    """Simple coin animation that jumps up then falls back down."""

    world_x: float
    world_y: float  # Bottom of the coin in world coordinates
    on_collect: Optional[Callable[[], None]] = None
    velocity_y: float = field(default=COIN_JUMP_VELOCITY, init=False)
    _start_y: float = field(init=False)
    _collected: bool = field(default=False, init=False)

    sprite_sheet: str = "background"
    sprite_name: str = "coin"

    def __post_init__(self) -> None:
        self._start_y = self.world_y

    def update(self, dt: float) -> bool:
        """Advance the coin's position."""
        # Integrate velocity.
        self.world_y += self.velocity_y * dt
        self.velocity_y -= COIN_GRAVITY * dt

        # When we fall back to or below the start height, mark complete.
        if self.world_y <= self._start_y:
            self.world_y = self._start_y
            if not self._collected and self.on_collect:
                self._collected = True
                self.on_collect()
            return False
        return True

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the coin relative to the camera."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        from ..content import sprites

        sprites.draw_at_position(
            surface,
            self.sprite_sheet,
            self.sprite_name,
            int(screen_x),
            int(screen_y),
        )
