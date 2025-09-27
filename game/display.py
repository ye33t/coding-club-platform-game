"""Display management with NES-style scaling."""

import pygame
from .constants import (
    NATIVE_WIDTH,
    NATIVE_HEIGHT,
    DEFAULT_SCALE,
    MIN_SCALE,
    MAX_SCALE,
    BLACK,
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
            vsync=1
        )
        pygame.display.set_caption("NES Platform Game")

        # Create native resolution surface for pixel-perfect rendering
        self.native_surface = pygame.Surface((NATIVE_WIDTH, NATIVE_HEIGHT))
        self.native_surface = self.native_surface.convert()

    def clear(self, color=BLACK):
        """Clear the native surface."""
        self.native_surface.fill(color)

    def present(self):
        """Scale and present the native surface to the screen."""
        # Scale up the native surface to window size (nearest neighbor for pixel-perfect)
        scaled = pygame.transform.scale(self.native_surface, (self.window_width, self.window_height))
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
                vsync=1
            )

    def get_native_surface(self):
        """Get the native resolution surface for drawing."""
        return self.native_surface