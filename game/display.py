"""Display management with NES-style scaling."""

import pygame

from .constants import (
    BLACK,
    DEFAULT_SCALE,
    MAX_SCALE,
    MIN_SCALE,
    NATIVE_HEIGHT,
    NATIVE_WIDTH,
)


class Display:
    """Manages the display surface with pixel-perfect scaling."""

    def __init__(self, scale=DEFAULT_SCALE):
        """Initialize display with given scale factor."""
        self.scale = max(MIN_SCALE, min(scale, MAX_SCALE))
        self.window_width = NATIVE_WIDTH * self.scale
        self.window_height = NATIVE_HEIGHT * self.scale

        # Create the window with V-sync enabled
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.DOUBLEBUF | pygame.HWSURFACE,
            vsync=1,
        )
        pygame.display.set_caption("NES Platform Game")

        # Create native resolution surface for pixel-perfect rendering
        # Use convert() to optimize the surface for fast blitting
        self.native_surface = pygame.Surface((NATIVE_WIDTH, NATIVE_HEIGHT)).convert()
        # Set the surface to use per-pixel alpha if needed
        self.native_surface.set_alpha(None)

    def clear(self, color=BLACK):
        """Clear the native surface."""
        self.native_surface.fill(color)

    def present(self):
        """Scale and present the native surface to the screen."""
        # Clear the screen first to prevent ghosting
        self.screen.fill(BLACK)
        # Scale up the native surface to window size using nearest neighbor
        # for pixel-perfect scaling. In pygame 2.1+, scale uses nearest
        # neighbor by default for integer scales
        scaled = pygame.transform.scale_by(self.native_surface, self.scale)
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def change_scale(self, delta):
        """Change the window scale by delta."""
        new_scale = max(MIN_SCALE, min(self.scale + delta, MAX_SCALE))
        if new_scale != self.scale:
            self.scale = new_scale
            self.window_width = NATIVE_WIDTH * self.scale
            self.window_height = NATIVE_HEIGHT * self.scale
            self.screen = pygame.display.set_mode(
                (self.window_width, self.window_height),
                pygame.DOUBLEBUF | pygame.HWSURFACE,
                vsync=1,
            )

    def get_native_surface(self):
        """Get the native resolution surface for drawing."""
        return self.native_surface
