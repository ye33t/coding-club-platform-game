"""Playing state - normal gameplay."""

import pygame

from ..input import Input
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

        # Check for warp trigger BEFORE physics
        if Input.is_down(keys):
            mario = game.world.mario
            if mario.state.on_ground:
                # Get tile below mario (the one he's standing on)
                from ..constants import TILE_SIZE

                tile_x = int(mario.state.x // TILE_SIZE)
                tile_y = int(mario.state.y // TILE_SIZE) - 1

                # Check for warp behavior
                instance = game.world.level.terrain_manager.get_instance(
                    mario.state.screen, tile_x, tile_y
                )
                if instance and instance.behavior:
                    from ..terrain import WarpBehavior

                    if isinstance(instance.behavior, WarpBehavior):
                        from .warp_enter import WarpEnterState

                        game.transition_to(WarpEnterState(instance.behavior))
                        return  # Skip physics this frame

        # Let the world process Mario's intent and update his state
        game.world.update(keys, dt)

    def draw(self, game, surface) -> None:
        """Draw everything to the screen during gameplay."""
        # Draw level tiles
        game._draw_level(surface)

        # Draw Mario at screen position (transform from world to screen)
        game._draw_mario(surface)
