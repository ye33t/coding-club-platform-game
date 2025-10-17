"""Generic sprite effect for scripted sequences."""

from __future__ import annotations

from dataclasses import dataclass

from pygame import Surface

from ..camera import Camera
from ..content import sprites
from .base import Effect


@dataclass
class SpriteEffect(Effect):
    """Static sprite effect with externally controlled position."""

    sprite_sheet: str
    sprite_name: str
    world_x: float
    world_y: float
    z_index: int = 0
    reflected: bool = False

    _active: bool = True

    def update(self, dt: float) -> bool:  # noqa: D401
        """Return whether the effect should remain active."""
        return self._active

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Draw the sprite at its current world position."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        sprites.draw_at_position(
            surface,
            self.sprite_sheet,
            self.sprite_name,
            int(screen_x),
            int(screen_y),
            self.reflected,
        )

    def set_position(self, x: float, y: float) -> None:
        """Update the sprite's world position."""
        self.world_x = x
        self.world_y = y

    def deactivate(self) -> None:
        """Mark the sprite for removal."""
        self._active = False
