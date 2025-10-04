"""None behavior for marker zones with no behavior."""

from .base import BehaviorContext, TerrainBehavior


class NoneBehavior(TerrainBehavior):
    """Marker behavior that does nothing.

    Used for zones that serve as markers (e.g., warp destinations)
    but don't have any tile-level behavior.
    """

    def process(self, context: BehaviorContext) -> None:
        """No-op processing."""
        pass
