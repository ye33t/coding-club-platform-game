"""Base interfaces for decorative props."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Prop(ABC):
    """Encapsulates long-lived decorative state within the world."""

    @abstractmethod
    def spawn(self, world) -> None:
        """Create any visuals or state required for this prop."""

    def reset(self, world) -> None:
        """Reset the prop back to its initial state."""
        self.destroy()
        self.spawn(world)

    def update(self, world, dt: float) -> None:
        """Advance the prop state. Override when animation is required."""
        return

    def destroy(self) -> None:
        """Tear down any resources associated with this prop."""
        return
