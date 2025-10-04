"""Warp exit state - Mario exiting pipe."""

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..game import Game
    from ..terrain import WarpBehavior


class WarpExitState(State):
    """State for animating mario coming up out of pipe."""

    def __init__(self, warp_behavior: "WarpBehavior"):
        """Initialize warp exit state.

        Args:
            warp_behavior: The warp behavior containing destination info
        """
        self.warp_behavior = warp_behavior
        self.distance_moved = 0.0

    def on_enter(self, game: "Game") -> None:
        """Setup exit: change screen, position mario at destination."""
        # Find destination pipe position
        center_x, pipe_y = game.world.level.find_zone_position(
            self.warp_behavior.to_screen, self.warp_behavior.to_zone
        )

        # Convert tile coords to pixel coords
        from ..constants import TILE_SIZE

        pixel_x = center_x * TILE_SIZE
        pixel_y = pipe_y * TILE_SIZE

        # Position mario at pipe, offset down by mario's height (hidden)
        warp_distance = game.world.mario.state.height
        game.world.mario.state.screen = self.warp_behavior.to_screen
        game.world.mario.state.x = pixel_x
        game.world.mario.state.y = pixel_y - warp_distance

        # Reset camera to follow mario at new position
        from ..constants import NATIVE_WIDTH

        screen_center = NATIVE_WIDTH // 2
        ideal_camera_x = max(0, pixel_x - screen_center)
        game.world.camera.state.x = ideal_camera_x
        game.world.camera.state.max_x = ideal_camera_x

        self.distance_moved = 0.0

        # Optional: Flash screen black here

    def handle_events(self, game: "Game") -> None:
        """No input during warp."""
        pass

    def update(self, game: "Game", dt: float) -> None:
        """Move mario up out of pipe."""
        from ..physics.config import WARP_SPEED

        warp_distance = game.world.mario.state.height
        move_amount = WARP_SPEED * dt
        game.world.mario.state.y += move_amount
        self.distance_moved += move_amount

        # When fully out of pipe, return to playing
        if self.distance_moved >= warp_distance:
            from .playing import PlayingState

            game.transition_to(PlayingState())

    def draw(self, game: "Game", surface) -> None:
        """Draw with mario behind tiles."""
        # Draw mario first (behind)
        game._draw_mario(surface)
        # Draw tiles on top
        game._draw_level(surface)
