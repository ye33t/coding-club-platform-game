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

        # Walking Mario animation state (now in pixels for smooth movement)
        self.mario_x = 0.0  # X position in pixels (float for smooth movement)
        self.mario_y = 16.0  # Y position in pixels from bottom (fixed at 2 tiles = 16 pixels)
        self.mario_frame = 0  # Current animation frame
        self.mario_anim_timer = 0.0  # Timer for animation
        self.mario_speed = 64.0  # Movement speed in pixels per second (8 tiles/sec * 8 pixels/tile)
        self.frame_duration = 6 / FPS  # Time per animation frame in seconds

        # Running Mario animation state
        self.running_mario_x = 0.0  # X position in pixels
        self.running_mario_y = 48.0  # Y position in pixels from bottom (6 tiles up)
        self.running_mario_frame = 0  # Current animation frame
        self.running_mario_anim_timer = 0.0  # Timer for animation
        self.running_mario_speed = 128.0  # Faster speed for running (12 tiles/sec)
        self.running_frame_duration = 3 / FPS  # Faster animation for running

        # Animation frames for walking
        self.walk_frames = [
            "small_mario_walk1",
            "small_mario_walk2",
        ]

        # Animation frames for running
        self.run_frames = [
            "small_mario_run1",
            "small_mario_run2",
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
        from .constants import NATIVE_WIDTH

        # Update walking Mario
        self.mario_x += self.mario_speed * dt
        if self.mario_x > NATIVE_WIDTH:
            self.mario_x = -16  # Start just off the left side (2 tiles width)

        # Update walking animation timer
        self.mario_anim_timer += dt
        if self.mario_anim_timer >= self.frame_duration:
            self.mario_anim_timer = 0.0
            self.mario_frame = (self.mario_frame + 1) % len(self.walk_frames)

        # Update running Mario
        self.running_mario_x += self.running_mario_speed * dt
        if self.running_mario_x > NATIVE_WIDTH:
            self.running_mario_x = -16  # Start just off the left side

        # Update running animation timer
        self.running_mario_anim_timer += dt
        if self.running_mario_anim_timer >= self.running_frame_duration:
            self.running_mario_anim_timer = 0.0
            self.running_mario_frame = (self.running_mario_frame + 1) % len(self.run_frames)

    def draw(self):
        """Draw everything to the screen."""
        # Clear the native surface
        self.display.clear(BACKGROUND_COLOR)

        # Get the surface to draw on
        surface = self.display.get_native_surface()

        # Draw walking Mario at pixel position for smooth movement
        current_sprite = self.walk_frames[self.mario_frame]
        sprites.draw_at_position(surface, "characters", current_sprite, int(self.mario_x), int(self.mario_y))

        # Draw running Mario above the walking one
        running_sprite = self.run_frames[self.running_mario_frame]
        sprites.draw_at_position(surface, "characters", running_sprite, int(self.running_mario_x), int(self.running_mario_y))

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