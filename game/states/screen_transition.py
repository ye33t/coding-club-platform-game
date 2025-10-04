"""Screen transition state - fades between states."""

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..game import Game


class ScreenTransitionState(State):
    """State for transitioning between states with a fade effect."""

    def __init__(self, next_state: State, duration: float = 0.3):
        """Initialize screen transition state.

        Args:
            next_state: The state to transition to after duration
            duration: Duration of transition in seconds (default 0.3s)
        """
        self.next_state = next_state
        self.duration = duration
        self.elapsed = 0.0

    def on_enter(self, game: "Game") -> None:
        """Reset timer when entering transition."""
        self.elapsed = 0.0

    def handle_events(self, game: "Game") -> None:
        """No input during transition."""
        pass

    def update(self, game: "Game", dt: float) -> None:
        """Update transition timer and switch when complete."""
        self.elapsed += dt

        # When duration complete, transition to next state
        if self.elapsed >= self.duration:
            game.transition_to(self.next_state)

    def draw(self, game: "Game", surface) -> None:
        """Draw transition (empty for now - visual to be designed)."""
        pass
