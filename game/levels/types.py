"""Shared types for level parsing."""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class ParserContext:
    """Context carried through parsing operations."""

    layout: List[str]  # The full screen layout (bottom-up)
    width: int
    height: int
    screen_index: int
    errors: List[str] = field(default_factory=list)

    def get_char(self, x: int, y: int) -> str | None:
        """Safe character access with bounds checking."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.layout[y][x]
        raise IndexError(
            (
                f"Coordinates ({x}, {y}) out of bounds "
                f"(width={self.width}, height={self.height})"
            )
        )

    def add_error(self, message: str) -> None:
        """Add an error message to the context."""
        self.errors.append(f"Screen {self.screen_index}: {message}")


@dataclass
class Compound:
    """Represents a connected group of the same character."""

    character: str  # The character that forms this compound
    mask: List[List[bool]]  # 2D mask where True = character present
    origin_x: int  # Left edge in world coordinates
    origin_y: int  # Bottom edge in world coordinates

    @property
    def width(self) -> int:
        """Width of the compound in tiles."""
        return len(self.mask[0]) if self.mask else 0

    @property
    def height(self) -> int:
        """Height of the compound in tiles."""
        return len(self.mask)

    @property
    def is_solid(self) -> bool:
        """Check if all cells in the mask are filled (no gaps)."""
        for row in self.mask:
            for cell in row:
                if not cell:
                    return False
        return True

    def is_top(self, y: int) -> bool:
        """Check if local y coordinate is at the top of the compound."""
        return y == self.height - 1

    def to_world(self, x: int, y: int) -> Tuple[int, int]:
        """Convert local coordinates to world coordinates."""
        return (self.origin_x + x, self.origin_y + y)
