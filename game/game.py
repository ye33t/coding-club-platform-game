"""Main game class with NES-style game loop."""

import os
import sys

import pygame

from .constants import (
    BACKGROUND_COLOR,
    FPS,
    SUB_TILE_SIZE,
    SUB_TILES_HORIZONTAL,
    SUB_TILES_VERTICAL,
    WHITE,
)
from .display import Display
from .sprites import sprites
from .states import PlayingState, State
from .world import World


class Game:
    """Main game class handling the game loop and state."""

    def __init__(self):
        """Initialize pygame and game components."""
        pygame.init()
        self.display = Display()
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_debug = False

        # Initialize font for debug info
        self.font = pygame.font.Font(None, 16)

        # Load sprite sheets
        assets_path = os.path.join(os.path.dirname(__file__), "assets", "images")
        sprites.load_sheets(assets_path)

        # Create World (owns level, mario, camera, physics)
        self.world = World()

        # Initialize state machine
        self.state: State = PlayingState()
        self.state.on_enter(self)
        
    def run(self):
        """Main game loop."""
        print("Starting NES Platform Game...")
        print("Controls:")
        print("  ESC   - Quit")
        print("  +/-   - Change Window Scale")
        print("  F3    - Toggle Debug Info")
        print("  Arrow Keys - Move Mario")
        print("  Shift - Run")
        print("  Space - Jump")

        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0

            # Global event handling
            self._handle_events()

            # State-specific event handling
            self.state.handle_events(self)

            # Update game state
            self.state.update(self, dt)

            # Clear screen and get surface
            self.display.clear(BACKGROUND_COLOR)
            surface = self.display.get_native_surface()

            # State-specific drawing
            self.state.draw(self, surface)

            # Global debug overlay
            if self.show_debug:
                self._draw_tile_grid(surface)
                self._draw_debug_info(surface)

            # Present the frame
            self.display.present()

        # Cleanup
        pygame.quit()
        sys.exit()

    def transition_to(self, new_state: State) -> None:
        """Transition to a new game state.

        Calls on_exit on current state, then on_enter on new state.

        Args:
            new_state: The state to transition to
        """
        self.state.on_exit(self)
        self.state = new_state
        self.state.on_enter(self)

    def _handle_events(self):
        """Handle global events (ESC, scaling, debug toggle)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self.display.change_scale(-1)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    self.display.change_scale(1)
                elif event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug

    def _draw_level(self, surface):
        """Draw the visible level tiles."""
        from .constants import TILE_SIZE

        # Get visible tiles from level
        visible_tiles = self.world.level.get_visible_tiles(
            self.world.mario.state.screen, self.world.camera.x
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            # Get tile definition
            tile_def = self.world.level.get_tile_definition(tile_type)
            if not tile_def or not tile_def["sprite_name"]:
                continue  # Skip empty tiles or tiles without sprites

            # Convert tile position to world pixels (each tile is 16x16 pixels)
            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            # Apply visual state from behaviors
            visual = self.world.level.get_tile_visual_state(
                self.world.mario.state.screen, tile_x, tile_y
            )
            if visual:
                world_y += visual.offset_y
                # Future: could add offset_x, rotation, scale, etc.

            # Transform to screen coordinates
            screen_x, screen_y = self.world.camera.world_to_screen(world_x, world_y)

            # Draw the tile sprite
            sprites.draw_at_position(
                surface,
                tile_def["sprite_sheet"],
                tile_def["sprite_name"],
                int(screen_x),
                int(screen_y),
            )

    def _draw_mario(self, surface):
        """Draw Mario at his screen position."""
        # Transform Mario's world position to screen position
        screen_x, screen_y = self.world.camera.world_to_screen(
            self.world.mario.state.x, self.world.mario.state.y
        )

        # Get sprite name
        sprite_name = self.world.mario._get_sprite_name()
        if sprite_name:
            # Use reflection when facing left
            reflected = not self.world.mario.state.facing_right

            # Draw at screen position (not world position)
            sprites.draw_at_position(
                surface,
                "characters",
                sprite_name,
                int(screen_x),
                int(screen_y),
                reflected,
            )

    def _draw_tile_grid(self, surface):
        """Draw the 8x8 tile grid for debugging."""
        # Draw vertical lines
        for x in range(0, SUB_TILES_HORIZONTAL + 1):
            pygame.draw.line(
                surface,
                (100, 100, 100),
                (x * SUB_TILE_SIZE, 0),
                (x * SUB_TILE_SIZE, SUB_TILES_VERTICAL * SUB_TILE_SIZE),
            )

        # Draw horizontal lines
        for y in range(0, SUB_TILES_VERTICAL + 1):
            pygame.draw.line(
                surface,
                (100, 100, 100),
                (0, y * SUB_TILE_SIZE),
                (SUB_TILES_HORIZONTAL * SUB_TILE_SIZE, y * SUB_TILE_SIZE),
            )

    def _draw_debug_info(self, surface):
        """Draw debug information."""
        fps = self.clock.get_fps()
        mario = self.world.mario.state
        debug_texts = [
            f"FPS: {fps:.1f}",
            f"Resolution: {surface.get_width()}x{surface.get_height()}",
            f"Scale: {self.display.scale}x",
            f"Camera X: {self.world.camera.x:.1f}",
            f"Mario World: ({mario.x:.1f}, {mario.y:.1f})",
            f"Velocity: ({mario.vx:.1f}, {mario.vy:.1f})",
            f"Action: {mario.action}",
            f"On Ground: {mario.on_ground}",
        ]

        y = 4
        for text in debug_texts:
            text_surface = self.font.render(text, True, WHITE)
            surface.blit(text_surface, (4, y))
            y += 12

    def quit(self):
        """Quit the game."""
        self.running = False
