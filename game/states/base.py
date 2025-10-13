"""Base class for game states."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import Game


class State(ABC):
    """Base class for all game states.

    States implement the game loop methods (handle_events, update, draw)
    and can request state transitions via game.transition().
    """

    def on_enter(self, game: "Game") -> None:
        """Called when transitioning INTO this state.

        Use this for setup, initialization, or state preparation.

        Args:
            game: The game context
        """
        pass

    def on_exit(self, game: "Game") -> None:
        """Called when transitioning OUT OF this state.

        Use this for cleanup or saving state.

        Args:
            game: The game context
        """
        pass

    @abstractmethod
    def update(self, game: "Game", dt: float) -> None:
        """Update game logic.

        Args:
            game: The game context
            dt: Time delta since last update in seconds
        """
        pass

    def draw(self, game: "Game", surface) -> None:
        """Render the current state.

        The surface is pre-cleared and ready to draw on.
        Do not call display.present() - that's handled by Game.run().

        Args:
            game: The game context
            surface: The pygame surface to draw on
        """
        game.render(surface)
