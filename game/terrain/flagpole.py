"""Flagpole behavior for end-of-level sequence."""

from typing import TYPE_CHECKING

from .base import BehaviorContext, TerrainBehavior

if TYPE_CHECKING:
    from ..level import Level


class FlagpoleBehavior(TerrainBehavior):
    """Flagpole behavior - triggers end-of-level sequence."""

    def process(self, context: BehaviorContext) -> None:
        """Process flagpole behavior (no animation - purely metadata).

        Args:
            context: The behavior context
        """
        pass  # Flagpole is handled by game states, not here

    def validate(self, level: "Level") -> None:
        """Validate exactly one flagpole exists in the entire level.

        Args:
            level: The fully loaded level

        Raises:
            ValueError: If there's not exactly one flagpole
        """
        # Find all flagpole instances across all screens
        flagpole_columns = set()

        for instance in level.terrain_manager.instances.values():
            if isinstance(instance.behavior, FlagpoleBehavior):
                # Track unique (screen, x) combinations
                flagpole_columns.add((instance.screen, instance.x))

        # Verify exactly one flagpole column exists
        if len(flagpole_columns) == 0:
            raise ValueError("No flagpole found in level")
        elif len(flagpole_columns) > 1:
            raise ValueError(
                f"Found {len(flagpole_columns)} flagpole columns in level, "
                "but exactly one is required"
            )
