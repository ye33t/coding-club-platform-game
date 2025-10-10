"""Warp enter state - Mario entering pipe."""

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..terrain.warp import WarpBehavior


class WarpEnterState(State):
    """State for animating mario going down into pipe."""

    def __init__(self, warp_behavior: "WarpBehavior"):
        """Initialize warp enter state.

        Args:
            warp_behavior: The warp behavior containing destination info
        """
        self.warp_behavior = warp_behavior
        self.distance_moved = 0.0

    def on_enter(self, game) -> None:
        """Start warp enter animation."""
        self.distance_moved = 0.0
        # Set Mario to render behind terrain
        game.world.mario.z_index = -10

    def handle_events(self, game) -> None:
        """No input during warp."""
        pass

    def on_exit(self, game) -> None:
        """Reset Mario's z_index when exiting warp."""
        game.world.mario.z_index = 20

    def update(self, game, dt: float) -> None:
        """Move mario down into pipe."""
        from ..physics.config import WARP_SPEED

        warp_distance = game.world.mario.state.height
        move_amount = WARP_SPEED * dt
        game.world.mario.state.y -= move_amount
        self.distance_moved += move_amount

        # When fully inside pipe, transition to exit
        if self.distance_moved >= warp_distance:
            from .screen_transition import ScreenTransitionState, TransitionMode
            from .warp_exit import WarpExitState

            next_state = WarpExitState(self.warp_behavior)
            game.transition_to(
                ScreenTransitionState(self, next_state, TransitionMode.BOTH)
            )

    def draw(self, game, surface) -> None:
        """Draw with mario behind tiles."""
        game.draw_world(surface)
