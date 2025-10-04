"""Screen transition state - fades between states."""

from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..game import Game


class ScreenTransitionState(State):
    """State for transitioning between states with a fade effect."""

    def __init__(self, next_state: State, duration: float = 2.0):
        """Initialize screen transition state.

        Args:
            next_state: The state to transition to after duration
            duration: Duration of full transition (fade out + fade in) in seconds
        """
        self.next_state = next_state
        self.duration = duration
        self.elapsed = 0.0
        self.midpoint_triggered = False

    def on_enter(self, game: "Game") -> None:
        """Reset timer when entering transition."""
        self.elapsed = 0.0
        self.midpoint_triggered = False

    def handle_events(self, game: "Game") -> None:
        """No input during transition."""
        pass

    def update(self, game: "Game", dt: float) -> None:
        """Update transition timer and switch when complete."""
        self.elapsed += dt

        # At midpoint (when fully black), trigger next state setup
        if not self.midpoint_triggered and self.elapsed >= self.duration / 2:
            self.midpoint_triggered = True
            self.next_state.on_enter(game)

        # When duration complete, transition to next state
        if self.elapsed >= self.duration:
            game.transition_to(self.next_state)

    def draw(self, game: "Game", surface) -> None:
        """Draw transition with shrinking circle iris effect."""
        # Draw game underneath (mario behind level during transition)
        game._draw_mario(surface)
        game._draw_level(surface)

        # Draw transition effect
        self._draw_transition_effect(surface)

    def _draw_transition_effect(self, surface) -> None:
        """Draw the circular iris transition effect."""
        import math

        import pygame

        from ..constants import BLACK, BACKGROUND_COLOR, NATIVE_HEIGHT, NATIVE_WIDTH

        # Calculate progress (0.0 to 1.0 over full duration)
        progress = min(1.0, self.elapsed / self.duration)

        # First half: fade out (0.0 to 0.5 -> shrink from max to 0)
        # Second half: fade in (0.5 to 1.0 -> expand from 0 to max)
        max_radius = math.sqrt((NATIVE_WIDTH / 2) ** 2 + (NATIVE_HEIGHT / 2) ** 2)

        if progress < 0.5:
            # Fade out: first half
            local_progress = progress * 2  # 0.0 to 1.0
            eased = local_progress * local_progress * (3 - 2 * local_progress)
            radius = max_radius * (1 - eased)  # Shrink to 0
        else:
            # Fade in: second half
            local_progress = (progress - 0.5) * 2  # 0.0 to 1.0
            eased = local_progress * local_progress * (3 - 2 * local_progress)
            radius = max_radius * eased  # Expand from 0

        # Create black mask with circular hole
        mask = pygame.Surface((NATIVE_WIDTH, NATIVE_HEIGHT))
        mask.fill(BLACK)

        # Draw circle in center (will be transparent - the "window" to see game)
        center = (NATIVE_WIDTH // 2, NATIVE_HEIGHT // 2)
        if radius > 0:
            pygame.draw.circle(mask, BACKGROUND_COLOR, center, int(radius))

        # Make the circle transparent (everything else stays black)
        mask.set_colorkey(BACKGROUND_COLOR)

        # Apply mask over game
        surface.blit(mask, (0, 0))
