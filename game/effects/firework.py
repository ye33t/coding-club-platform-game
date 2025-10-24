"""Animated firework burst used during the castle finale."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pygame import Surface

from game.constants import FPS

from ..camera import Camera
from ..content import sprites
from .base import Effect

_FRAME_NAMES = ("firework_1", "firework_2", "firework_3")
_FRAME_INTERVAL = 20 / FPS  # Display each frame for ~0.33 seconds.


@dataclass(slots=True)
class FireworkEffect(Effect):
    """Cycle through the firework sprite trio once, then expire."""

    world_x: float
    world_y: float
    z_index: int = 0
    on_finished: Callable[[], None] | None = None

    _frame_index: int = 0
    _elapsed: float = 0.0
    _hold_completed: bool = False

    def update(self, dt: float) -> bool:  # noqa: D401
        """Advance the animation and deactivate after the final hold."""
        self._elapsed += dt
        while self._elapsed >= _FRAME_INTERVAL:
            self._elapsed -= _FRAME_INTERVAL
            if self._frame_index < len(_FRAME_NAMES) - 1:
                self._frame_index += 1
            else:
                if self._hold_completed:
                    if self.on_finished is not None:
                        self.on_finished()
                        self.on_finished = None
                    return False
                self._hold_completed = True
        return True

    def draw(self, surface: Surface, camera: Camera) -> None:
        """Render the current firework frame."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        sprites.draw_at_position(
            surface,
            "objects",
            _FRAME_NAMES[self._frame_index],
            int(screen_x),
            int(screen_y),
        )
