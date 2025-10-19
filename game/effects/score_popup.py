"""Floating score popup effect shown after earning points."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from pygame import Surface

from ..camera import Camera
from ..constants import FPS, NATIVE_HEIGHT, SUB_TILE_SIZE
from ..content import sprites
from ..gameplay import (
    SCORE_POPUP_LIFETIME_FRAMES,
    SCORE_POPUP_UPWARD_SPEED,
    SCORE_POPUP_VERTICAL_OFFSET,
)
from .base import Effect


@dataclass
class ScorePopupEffect(Effect):
    """Display a score label that drifts upward before disappearing."""

    label: str
    world_x: float
    world_y: float
    horizontal_velocity: float
    upward_speed: float = SCORE_POPUP_UPWARD_SPEED
    lifetime_frames: int = SCORE_POPUP_LIFETIME_FRAMES
    vertical_offset: float = SCORE_POPUP_VERTICAL_OFFSET
    z_index: int = 90

    _elapsed: float = 0.0
    _lifetime: float = field(init=False)
    _sprite_surface: Optional[Surface] = field(init=False, default=None)
    _text_surfaces: List[Surface] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self._lifetime = max(0.0, self.lifetime_frames / FPS)
        self.world_y += self.vertical_offset
        self._sprite_surface = sprites.get_with_palette("scores", self.label)
        if self._sprite_surface is None:
            self._text_surfaces = self._build_text_surfaces(self.label)

    def update(self, dt: float) -> bool:
        """Advance the popup motion."""
        self._elapsed += dt
        if self._elapsed >= self._lifetime:
            return False

        self.world_x += self.horizontal_velocity * dt
        self.world_y += self.upward_speed * dt
        return True

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the popup at its current position."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        draw_base_y = NATIVE_HEIGHT - int(screen_y)

        if self._sprite_surface is not None:
            sprite_width = self._sprite_surface.get_width()
            sprite_height = self._sprite_surface.get_height()
            draw_x = int(screen_x) - sprite_width // 2
            draw_y = draw_base_y - sprite_height
            surface.blit(self._sprite_surface, (draw_x, draw_y))
            return

        if not self._text_surfaces:
            return

        total_width = len(self._text_surfaces) * SUB_TILE_SIZE
        draw_x = int(screen_x) - total_width // 2
        draw_y = draw_base_y - SUB_TILE_SIZE
        for idx, glyph_surface in enumerate(self._text_surfaces):
            surface.blit(glyph_surface, (draw_x + idx * SUB_TILE_SIZE, draw_y))

    @staticmethod
    def _build_text_surfaces(label: str) -> List[Surface]:
        """Construct fallback glyph surfaces for labels without dedicated sprites."""
        surfaces: List[Surface] = []
        for char in label:
            glyph = sprites.get_with_palette("text", char.lower())
            if glyph is None:
                continue
            surfaces.append(glyph)
        return surfaces
