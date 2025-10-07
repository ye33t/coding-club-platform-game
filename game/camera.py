"""Camera system for viewport management."""

from copy import deepcopy
from dataclasses import dataclass

from .constants import NATIVE_WIDTH


@dataclass
class CameraState:
    """Camera's mutable state that can be cloned and modified."""

    x: float = 0.0  # Current camera position (left edge of viewport)
    max_x: float = 0.0  # Maximum x position reached (ratchet mechanism)

    def clone(self) -> "CameraState":
        """Create a deep copy of this camera state."""
        return deepcopy(self)


class Camera:
    """Manages the viewport for horizontal scrolling."""

    def __init__(self) -> None:
        """Initialize camera at world origin."""
        self.state: CameraState = CameraState()

    def apply_state(self, new_state: CameraState) -> None:
        """Apply a new camera state.

        Args:
            new_state: The new camera state to apply
        """
        self.state = new_state

    def update(self, mario_world_x: float, level_width: float) -> None:
        """Update camera position based on Mario's position.

        Scrolling rules:
        1. Keep Mario at screen center when moving forward
        2. Never scroll backward (ratchet mechanism)
        3. Stop at level boundaries

        Args:
            mario_world_x: Mario's x position in world coordinates
            level_width: Total width of the level
        """
        # Calculate ideal camera position to keep Mario centered
        screen_center = NATIVE_WIDTH // 2  # 128 pixels
        ideal_camera_x = mario_world_x - screen_center

        # Apply constraints
        # 1. Can't go below 0 (left edge of level)
        ideal_camera_x = max(0, ideal_camera_x)

        # 2. Can't go beyond level width - screen width (right edge)
        max_camera_x = max(0, level_width - NATIVE_WIDTH)
        ideal_camera_x = min(ideal_camera_x, max_camera_x)

        # 3. Apply ratchet mechanism (never scroll backward)
        if ideal_camera_x > self.state.max_x:
            self.state.max_x = ideal_camera_x
            self.state.x = ideal_camera_x
        else:
            # Can't scroll back, but Mario can move within current view
            self.state.x = self.state.max_x

    def world_to_screen(self, world_x: float, world_y: float) -> tuple[float, float]:
        """Transform world coordinates to screen coordinates.

        Args:
            world_x: X position in world space
            world_y: Y position in world space

        Returns:
            (screen_x, screen_y) in screen space
        """
        screen_x = world_x - self.state.x
        return screen_x, world_y  # Y doesn't change (no vertical scrolling)

    def screen_to_world(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        """Transform screen coordinates to world coordinates.

        Args:
            screen_x: X position in screen space
            screen_y: Y position in screen space

        Returns:
            (world_x, world_y) in world space
        """
        world_x = screen_x + self.state.x
        return world_x, screen_y  # Y doesn't change

    def is_visible(self, world_x: float, width: float) -> bool:
        """Check if an object is visible in the current viewport.

        Args:
            world_x: X position of object in world space
            width: Width of the object

        Returns:
            True if any part of object is visible
        """
        return bool(
            world_x + width >= self.state.x and world_x <= self.state.x + NATIVE_WIDTH
        )

    @property
    def x(self) -> float:
        """Get current camera x position (backward compatibility)."""
        return self.state.x

    @x.setter
    def x(self, value: float) -> None:
        """Set camera x position (backward compatibility)."""
        self.state.x = value

    @property
    def max_x(self) -> float:
        """Get maximum x reached (backward compatibility)."""
        return self.state.max_x

    @max_x.setter
    def max_x(self, value: float) -> None:
        """Set maximum x reached (backward compatibility)."""
        self.state.max_x = value
