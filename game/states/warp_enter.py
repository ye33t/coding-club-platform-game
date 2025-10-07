"""Warp enter state - Mario entering pipe."""

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..terrain import WarpBehavior


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

    def handle_events(self, game) -> None:
        """No input during warp."""
        pass

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
        game.draw_background(surface)
        # Draw mario first (behind)
        game.draw_mario(surface)
        # Draw tiles on top
        game.draw_terrain(surface)
