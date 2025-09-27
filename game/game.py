"""Main game class with NES-style game loop."""

import pygame
import sys
import os
from .display import Display
from .constants import FPS, BACKGROUND_COLOR, WHITE, TILES_HORIZONTAL, TILES_VERTICAL, TILE_SIZE
from .sprites import sprites


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

        # Format: (sprite_name, tile_x, tile_y) where y is from bottom of screen
        # y=0 is the very bottom, y=27 is the top (screen is 28 tiles tall)
        self.test_sprites = [
            ("small_mario_stand", 6, 2),   # Mario standing 2 tiles from bottom
        ]

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
        # Game logic will go here
        pass

    def draw(self):
        """Draw everything to the screen."""
        # Clear the native surface
        self.display.clear(BACKGROUND_COLOR)

        # Get the surface to draw on
        surface = self.display.get_native_surface()

        # Draw test sprites using tile coordinates
        for item in self.test_sprites:
            sprite_name, tile_x, tile_y = item
            # Determine which sheet the sprite belongs to
            if "mario" in sprite_name or "luigi" in sprite_name or "peach" in sprite_name:
                sheet = "characters"
            elif "goomba" in sprite_name or "koopa" in sprite_name:
                sheet = "enemies"
            elif "coin" in sprite_name or "mushroom" in sprite_name or "star" in sprite_name:
                sheet = "other"
            else:
                sheet = "characters"  # default

            # Draw sprite at tile position (bottom-aligned)
            sprites.draw_at_tile(surface, sheet, sprite_name, tile_x, tile_y)

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
            pygame.draw.line(surface, (100, 100, 100),
                           (x * TILE_SIZE, 0),
                           (x * TILE_SIZE, TILES_VERTICAL * TILE_SIZE))

        # Draw horizontal lines
        for y in range(0, TILES_VERTICAL + 1):
            pygame.draw.line(surface, (100, 100, 100),
                           (0, y * TILE_SIZE),
                           (TILES_HORIZONTAL * TILE_SIZE, y * TILE_SIZE))

    def draw_debug_info(self, surface):
        """Draw debug information."""
        fps = self.clock.get_fps()
        debug_texts = [
            f"FPS: {fps:.1f}",
            f"Resolution: {surface.get_width()}x{surface.get_height()}",
            f"Tiles: {TILES_HORIZONTAL}x{TILES_VERTICAL}",
            f"Scale: {self.display.scale}x",
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
        print("  ESC - Quit")
        print("  +/- - Change Window Scale")
        print("  F3  - Toggle Debug Info")

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