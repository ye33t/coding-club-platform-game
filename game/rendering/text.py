"""Utility helpers for drawing HUD-styled text."""

from __future__ import annotations

from ..constants import NATIVE_WIDTH, SUB_TILE_SIZE
from ..content import sprites

_SUPPORTED_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-*!.,©x ")


def glyph_for_char(char: str) -> str | None:
    """Translate a character to the NES text sprite name."""
    lowered = char.lower()
    if lowered in _SUPPORTED_CHARS:
        if lowered == " ":
            return None
        return lowered
    return None


def text_width(text: str) -> int:
    """Compute the pixel width consumed by the given text."""
    width = 0
    for char in text:
        width += SUB_TILE_SIZE
    return width


def draw_text(surface, text: str, start_x: int, y: int) -> None:
    """Draw glyph-aligned text using the HUD font sheet."""
    x = start_x
    for char in text:
        if char == " ":
            x += SUB_TILE_SIZE
            continue
        sprite_name = glyph_for_char(char)
        if sprite_name is None:
            x += SUB_TILE_SIZE
            continue
        sprites.draw_at_position(surface, "text", sprite_name, x, y)
        x += SUB_TILE_SIZE


def draw_centered_text(surface, text: str, y: int) -> None:
    """Draw text horizontally centered on the native viewport."""
    width = text_width(text)
    start_x = (NATIVE_WIDTH - width) // 2
    draw_text(surface, text, start_x, y)
