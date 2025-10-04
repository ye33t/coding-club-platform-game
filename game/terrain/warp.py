"""Warp behavior for pipe teleportation."""

from typing import TYPE_CHECKING

from .base import BehaviorContext, TerrainBehavior

if TYPE_CHECKING:
    from ..level import Level


class WarpBehavior(TerrainBehavior):
    """Warp pipe behavior - teleports mario to destination zone."""

    def __init__(self, to_screen: int, to_zone: str):
        """Initialize warp behavior.

        Args:
            to_screen: Destination screen index
            to_zone: Destination zone character
        """
        self.to_screen = to_screen
        self.to_zone = to_zone

    def process(self, context: BehaviorContext) -> None:
        """Process warp behavior (no animation - purely metadata).

        Args:
            context: The behavior context
        """
        pass  # Warp is handled by game states, not here

    def validate(self, level: "Level") -> None:
        """Validate warp target exists, is 1 tile high, and contiguous.

        Args:
            level: The fully loaded level

        Raises:
            ValueError: If warp target is invalid
        """
        # Check screen exists
        if self.to_screen not in level.zones:
            raise ValueError(f"Warp target screen {self.to_screen} not found")

        # Find all tiles with target zone
        zones = level.zones[self.to_screen]
        positions = [
            (x, y)
            for y in range(len(zones))
            for x in range(len(zones[0]))
            if zones[y][x] == self.to_zone
        ]

        if not positions:
            raise ValueError(
                f"Warp target zone '{self.to_zone}' not found "
                f"on screen {self.to_screen}"
            )

        # Validate height = 1 tile
        y_coords = {y for x, y in positions}
        if len(y_coords) != 1:
            raise ValueError(
                f"Warp target zone '{self.to_zone}' must be exactly 1 tile high, "
                f"found on rows: {sorted(y_coords)}"
            )

        # Validate contiguous (no gaps)
        x_coords = sorted([x for x, y in positions])
        min_x, max_x = x_coords[0], x_coords[-1]
        expected_tiles = max_x - min_x + 1
        if len(x_coords) != expected_tiles:
            raise ValueError(
                f"Warp target zone '{self.to_zone}' tiles must be contiguous, "
                f"found gaps in horizontal span [{min_x}, {max_x}]"
            )
