"""Main game class with NES-style game loop."""

import os
import sys

import pygame

from .constants import (
    BACKGROUND_COLOR,
    FPS,
    TILE_SIZE,
    TILES_HORIZONTAL,
    TILES_VERTICAL,
    WHITE,
)
from .display import Display
from .mario import Mario, MarioState
from .sprites import sprites
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
        assets_path = os.path.join(os.path.dirname(__file__), "assets")
        sprites.load_sheets(assets_path)

        # Create Mario and World
        self.mario = Mario(MarioState(x=50.0, y=16.0))  # Start Mario at x=50
        self.world = World()

    def handle_events(self):
        """Process pygame events."""
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

    def update(self, dt):
        """Update game state."""
        # Get current keyboard state
        keys = pygame.key.get_pressed()

        # Let the world process Mario's intent and update his state
        self.world.process_mario(self.mario, keys, dt)

    def draw(self):
        """Draw everything to the screen."""
        # Clear the native surface
        self.display.clear(BACKGROUND_COLOR)

        # Get the surface to draw on
        surface = self.display.get_native_surface()

        # Draw Mario using his own draw method
        self.mario.draw(surface)

        # Draw tile grid (for visualization)
        if self.show_debug:
            self.draw_tile_grid(surface)
            self.draw_debug_info(surface)

        # Present the scaled result
        self.display.present()

    def draw_tile_grid(self, surface):
        """Draw the 8x8 tile grid for debugging."""
        # Draw vertical lines
        for x in range(0, TILES_HORIZONTAL + 1):
            pygame.draw.line(
                surface,
                (100, 100, 100),
                (x * TILE_SIZE, 0),
                (x * TILE_SIZE, TILES_VERTICAL * TILE_SIZE),
            )

        # Draw horizontal lines
        for y in range(0, TILES_VERTICAL + 1):
            pygame.draw.line(
                surface,
                (100, 100, 100),
                (0, y * TILE_SIZE),
                (TILES_HORIZONTAL * TILE_SIZE, y * TILE_SIZE),
            )

    def draw_debug_info(self, surface):
        """Draw debug information."""
        fps = self.clock.get_fps()
        debug_texts = [
            f"FPS: {fps:.1f}",
            f"Resolution: {surface.get_width()}x{surface.get_height()}",
            f"Tiles: {TILES_HORIZONTAL}x{TILES_VERTICAL}",
            f"Scale: {self.display.scale}x",
            f"Mario: ({self.mario.state.x:.1f}, {self.mario.state.y:.1f})",
            f"Velocity: ({self.mario.state.vx:.1f}, {self.mario.state.vy:.1f})",
            f"Action: {self.mario.state.action}",
            f"On Ground: {self.mario.state.on_ground}",
        ]

        y = 4
        for text in debug_texts:
            text_surface = self.font.render(text, True, WHITE)
            surface.blit(text_surface, (4, y))
            y += 12

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

            # Game loop steps
            self.handle_events()
            self.update(dt)
            self.draw()

        # Cleanup
        pygame.quit()
        sys.exit()

    def quit(self):
        """Quit the game."""
        self.running = False
