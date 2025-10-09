"""Playing state - normal gameplay."""

import pygame

from ..physics.events import DeathEvent, EndLevelEvent, WarpEvent
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
            elif isinstance(event, EndLevelEvent):
                from .end_level import EndLevelState

                game.transition_to(
                    EndLevelState(event.flagpole_x, event.flagpole_base_y)
                )

    def draw(self, game, surface) -> None:
        """Draw everything to the screen during gameplay."""
        game.draw_background(surface)
        game.draw_terrain(surface)
        game.draw_effects(surface)
        game.draw_entities(surface)
        game.draw_mario(surface)
