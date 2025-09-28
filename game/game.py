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

        # Draw level tiles
        self.draw_level(surface)

        # Draw Mario at screen position (transform from world to screen)
        self.draw_mario(surface)

        # Draw tile grid (for visualization)
        if self.show_debug:
            self.draw_tile_grid(surface)
            self.draw_debug_info(surface)

        # Present the scaled result
        self.display.present()

    def draw_level(self, surface):
        """Draw the visible level tiles."""
        # Get visible tiles from level
        visible_tiles = self.world.level.get_visible_tiles(self.world.camera.x)

        from .constants import NATIVE_HEIGHT
        from .level import TILE_SLOPE_DOWN, TILE_SLOPE_UP

        for tile_x, tile_y, tile_type in visible_tiles:
            # Convert tile position to world pixels
            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            # Transform to screen coordinates
            screen_x, screen_y = self.world.camera.world_to_screen(world_x, world_y)

            # Remember: screen_y is from bottom, need to convert for pygame
            pygame_y = NATIVE_HEIGHT - screen_y - TILE_SIZE

            # Choose color based on tile type
            if tile_type == 1:  # TILE_GROUND
                color = (139, 69, 19)  # Brown
            elif tile_type == 2:  # TILE_BRICK
                color = (178, 34, 34)  # Brick red
            else:
                color = (100, 100, 100)  # Gray

            # Draw the tile shape
            if tile_type == TILE_SLOPE_UP:
                # 45° slope ascending left to right
                # Triangle: bottom-left, bottom-right, top-right
                points = [
                    (screen_x, pygame_y + TILE_SIZE),  # bottom-left
                    (screen_x + TILE_SIZE, pygame_y + TILE_SIZE),  # bottom-right
                    (screen_x + TILE_SIZE, pygame_y),  # top-right
                ]
                pygame.draw.polygon(surface, color, points)
            elif tile_type == TILE_SLOPE_DOWN:
                # 45° slope descending left to right
                # Triangle: bottom-left, bottom-right, top-left
                points = [
                    (screen_x, pygame_y + TILE_SIZE),  # bottom-left
                    (screen_x + TILE_SIZE, pygame_y + TILE_SIZE),  # bottom-right
                    (screen_x, pygame_y),  # top-left
                ]
                pygame.draw.polygon(surface, color, points)
            else:
                # Regular rectangle for other tiles
                pygame.draw.rect(
                    surface, color, (screen_x, pygame_y, TILE_SIZE, TILE_SIZE)
                )

    def draw_mario(self, surface):
        """Draw Mario at his screen position."""
        # Transform Mario's world position to screen position
        screen_x, screen_y = self.world.camera.world_to_screen(
            self.mario.state.x, self.mario.state.y
        )

        # Get sprite name
        sprite_name = self.mario._get_sprite_name()
        if sprite_name:
            # Use reflection when facing left
            reflected = not self.mario.state.facing_right

            # Draw at screen position (not world position)
            sprites.draw_at_position(
                surface,
                "characters",
                sprite_name,
                int(screen_x),
                int(screen_y),
                reflected,
            )

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
            f"Camera X: {self.world.camera.x:.1f}",
            f"Mario World: ({self.mario.state.x:.1f}, {self.mario.state.y:.1f})",
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
