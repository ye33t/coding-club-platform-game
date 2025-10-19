"""HUD render layer that draws score, coins, world label, and timer."""

from __future__ import annotations

from typing import Optional

from ..constants import NATIVE_HEIGHT, SUB_TILE_SIZE
from ..content import sprites
from .base import RenderContext, RenderLayer


class HudLayer(RenderLayer):
    """Render the static HUD at the top of the screen."""

    SCORE_COLUMN = 3
    COIN_COLUMN = 11
    WORLD_COLUMN = 18
    TIME_COLUMN = 25

    def __init__(self) -> None:
        self._font_sheet = "text"
        self._coin_sheet = "hud_coin"
        self._coin_frames = ("coin_1", "coin_2", "coin_3", "coin_2")
        self._top_row_y = NATIVE_HEIGHT - 3 * SUB_TILE_SIZE
        self._bottom_row_y = self._top_row_y - SUB_TILE_SIZE

    def draw(self, context: RenderContext) -> None:
        surface = context.surface
        hud = context.world.hud

        # Left block: name + score
        self._draw_text(
            surface, "MARIO", self._column_to_x(self.SCORE_COLUMN), self._top_row_y
        )
        self._draw_text(
            surface,
            hud.formatted_score(),
            self._column_to_x(self.SCORE_COLUMN),
            self._bottom_row_y,
        )

        # Center block: animated coin + count
        self._draw_coin(surface, context.world.animation_tick)
        self._draw_text(
            surface,
            "*",
            self._column_to_x(self.COIN_COLUMN + 1),
            self._bottom_row_y,
        )
        self._draw_text(
            surface,
            hud.formatted_coins(),
            self._column_to_x(self.COIN_COLUMN + 2),
            self._bottom_row_y,
        )

        # Right block: world label + timer
        self._draw_text(
            surface,
            "WORLD",
            self._column_to_x(self.WORLD_COLUMN),
            self._top_row_y,
        )
        world_label = hud.level_label or ""
        if world_label:
            self._draw_text(
                surface,
                world_label,
                self._column_to_x(self.WORLD_COLUMN + 1),
                self._bottom_row_y,
            )

        self._draw_text(
            surface,
            "TIME",
            self._column_to_x(self.TIME_COLUMN),
            self._top_row_y,
        )
        self._draw_text(
            surface,
            hud.formatted_timer(),
            self._column_to_x(self.TIME_COLUMN + 1),
            self._bottom_row_y,
        )

    def _draw_text(self, surface, text: str, start_x: int, y: int) -> None:
        x = start_x
        for char in text:
            if char == " ":
                x += SUB_TILE_SIZE
                continue
            sprite_name = self._glyph_for_char(char)
            if sprite_name is None:
                x += SUB_TILE_SIZE
                continue
            sprites.draw_at_position(surface, self._font_sheet, sprite_name, x, y)
            x += SUB_TILE_SIZE

    def _draw_coin(self, surface, animation_tick: int) -> None:
        frame_index = (animation_tick // 8) % len(self._coin_frames)
        sprite_name = self._coin_frames[frame_index]
        sprites.draw_at_position(
            surface,
            self._coin_sheet,
            sprite_name,
            self._column_to_x(self.COIN_COLUMN),
            self._bottom_row_y,
        )

    @staticmethod
    def _glyph_for_char(char: str) -> Optional[str]:
        lowered = char.lower()
        if lowered.isalnum() or lowered in {"-", "*", "!", ".", "©", "x"}:
            return lowered
        return None

    @staticmethod
    def _column_to_x(column: int) -> int:
        return column * SUB_TILE_SIZE
