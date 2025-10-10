"""Main game class with NES-style game loop."""

import os
import sys

import pygame

from .constants import BACKGROUND_COLOR, FPS, SUB_TILE_SIZE, TILE_SIZE, WHITE
from .content import sprites
from .display import Display
from .states import InitialState, State
from .world import World


class Game:
    """Main game class handling the game loop and state."""

    def __init__(self) -> None:
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

        # Initialize state machine with initial black screen
        self.state: State = InitialState()
        self.state.on_enter(self)

    def run(self) -> None:
        """Main game loop."""
        print("Starting NES Platform Game...")
        print("Controls:")
        print("  ESC   - Quit")
        print("  +/-   - Change Window Scale")
        print("  F3    - Toggle Debug Info")
        print("  WASD  - Move Mario")
        print("  J     - Run")
        print("  K     - Jump")

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

    def _handle_events(self) -> None:
        """Handle global events (ESC, scaling, debug toggle)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from .states.start_level import StartLevelState

                    self.transition_to(StartLevelState())
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self.display.change_scale(-1)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    self.display.change_scale(1)
                elif event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug

    def draw_background(self, surface: pygame.Surface) -> None:
        """Draw the visible background tiles."""
        visible_tiles = self.world.level.get_visible_background_tiles(
            self.world.mario.state.screen, self.world.camera.x
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            tile_def = self.world.level.get_tile_definition(tile_type)
            if not tile_def or not tile_def.sprite_name:
                continue

            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            screen_x, screen_y = self.world.camera.world_to_screen(world_x, world_y)

            sprites.draw_at_position(
                surface,
                tile_def.sprite_sheet,
                tile_def.sprite_name,
                int(screen_x),
                int(screen_y),
            )

    def draw_terrain(self, surface: pygame.Surface) -> None:
        """Draw the visible terrain tiles."""
        # Get visible tiles from level
        visible_tiles = self.world.level.get_visible_terrain_tiles(
            self.world.mario.state.screen, self.world.camera.x
        )

        for tile_x, tile_y, tile_type in visible_tiles:
            # Get tile definition
            tile_def = self.world.level.get_tile_definition(tile_type)
            if not tile_def or not tile_def.sprite_name:
                continue  # Skip empty tiles or tiles without sprites

            # Convert tile position to world pixels (each tile is 16x16 pixels)
            world_x = tile_x * TILE_SIZE
            world_y = tile_y * TILE_SIZE

            # Apply visual state from behaviors
            visual = self.world.level.get_terrain_tile_visual_state(
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
                tile_def.sprite_sheet,
                tile_def.sprite_name,
                int(screen_x),
                int(screen_y),
            )

    def draw_effects(self, surface: pygame.Surface) -> None:
        """Draw transient effects like coins."""
        self.world.effects.draw(surface, self.world.camera)

    def draw_entities(self, surface: pygame.Surface) -> None:
        """Draw active entities like mushrooms and enemies."""
        self.world.entities.draw(surface, self.world.camera)

    def draw_mario(self, surface: pygame.Surface) -> None:
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

    def draw_world(self, surface: pygame.Surface) -> None:
        """Draw the entire world using z-index based rendering.

        Render order:
        1. Background (fixed)
        2. Drawables with negative z-index (sorted, behind terrain)
        3. Terrain (fixed)
        4. Drawables with zero/positive z-index (sorted, in front of terrain)
        """
        # Get all drawables
        drawables = self.world.get_drawables()

        # Split into behind and front based on z-index
        behind = sorted(
            [d for d in drawables if d.z_index < 0], key=lambda d: d.z_index
        )
        front = sorted(
            [d for d in drawables if d.z_index >= 0], key=lambda d: d.z_index
        )

        # Render in order
        self.draw_background(surface)

        for drawable in behind:
            drawable.draw(surface, self.world.camera)

        self.draw_terrain(surface)

        for drawable in front:
            drawable.draw(surface, self.world.camera)

    def _draw_tile_grid(self, surface: pygame.Surface) -> None:
        """Draw the 8x8 tile grid for debugging."""
        width = surface.get_width()
        height = surface.get_height()
        camera_x = self.world.camera.x

        # Draw vertical lines aligned to world grid
        offset_x = -(camera_x % SUB_TILE_SIZE)
        x = offset_x
        while x <= width:
            if x >= 0:
                pygame.draw.line(
                    surface, (100, 100, 100), (int(x), 0), (int(x), height)
                )
            x += SUB_TILE_SIZE

        # Draw horizontal lines (camera does not scroll vertically yet)
        y = 0
        while y <= height:
            pygame.draw.line(surface, (100, 100, 100), (0, int(y)), (width, int(y)))
            y += SUB_TILE_SIZE

    def _draw_debug_info(self, surface: pygame.Surface) -> None:
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

    def quit(self) -> None:
        """Quit the game."""
        self.running = False
