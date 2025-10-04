"""Factory for creating terrain behaviors from configuration."""

from typing import Dict, Type

from .base import TerrainBehavior
from .bounce import BounceBehavior


class BehaviorFactoryError(Exception):
    """Exception raised when behavior creation fails."""

    pass


class BehaviorFactory:
    """Factory for creating terrain behavior instances from configuration."""

    def __init__(self):
        """Initialize the factory with registered behavior types."""
        self._registry: Dict[str, Type[TerrainBehavior]] = {
            "bounce": BounceBehavior,
        }

    def create(self, behavior_type: str) -> TerrainBehavior:
        """Create a behavior instance from a type string.

        Args:
            behavior_type: The type of behavior to create (e.g., "bounce")

        Returns:
            An instance of the requested behavior

        Raises:
            BehaviorFactoryError: If behavior type is unknown
        """
        if behavior_type not in self._registry:
            available = ", ".join(sorted(self._registry.keys()))
            raise BehaviorFactoryError(
                f"Unknown behavior type '{behavior_type}'. "
                f"Available types: {available}"
            )

        behavior_class = self._registry[behavior_type]
        return behavior_class()
