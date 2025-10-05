"""Playing state - normal gameplay."""

import pygame

from ..physics.events import DeathEvent, WarpEvent
from .base import State


class PlayingState(State):
    """State for normal gameplay.

    Handles player input, world updates, and rendering during active play.
    """

    def handle_events(self, game) -> None:
        """Process state-specific events during gameplay.

        Global events (ESC, +/-, F3) are handled by Game._handle_events().
        """
        pass  # No state-specific events yet

    def update(self, game, dt: float) -> None:
        """Update game state during gameplay."""
        # Get current keyboard state
        keys = pygame.key.get_pressed()

        # Let the world process Mario's intent and update his state
        # This may return a physics event (death, warp, etc.)
        event = game.world.update(keys, dt)

        # Handle physics events
        if event is not None:
            if isinstance(event, DeathEvent):
                from .death import DeathState

                game.transition_to(DeathState())
            elif isinstance(event, WarpEvent):
                from .warp_enter import WarpEnterState

                game.transition_to(WarpEnterState(event.warp_behavior))

    def draw(self, game, surface) -> None:
        """Draw everything to the screen during gameplay."""
        # Draw level tiles
        game._draw_level(surface)

        # Draw Mario at screen position (transform from world to screen)
        game._draw_mario(surface)
