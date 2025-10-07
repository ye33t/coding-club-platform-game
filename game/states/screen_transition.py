"""Screen transition state - fades between states."""

from enum import Enum
from typing import TYPE_CHECKING

from .base import State

if TYPE_CHECKING:
    from ..game import Game


class TransitionMode(Enum):
    """Transition animation mode."""

    FADE_IN = "fade_in"  # Only fade in from black
    FADE_OUT = "fade_out"  # Only fade out to black
    BOTH = "both"  # Fade out then fade in


class ScreenTransitionState(State):
    """State for transitioning between states with a fade effect."""

    TRANSITION_DURATION = 2.0

    def __init__(
        self,
        from_state: State,
        to_state: State,
        mode: TransitionMode = TransitionMode.BOTH,
    ):
        """Initialize screen transition state.

        Args:
            from_state: The state to transition from (shown before midpoint)
            to_state: The state to transition to (shown after midpoint)
            mode: Transition mode (FADE_IN, FADE_OUT, or BOTH)
        """
        self.from_state = from_state
        self.to_state = to_state
        self.mode = mode
        self.elapsed = 0.0
        self.midpoint_triggered = False

    def on_enter(self, game: "Game") -> None:
        """Reset timer when entering transition."""
        self.elapsed = 0.0
        self.midpoint_triggered = False

        # For FADE_IN, initialize to_state immediately
        if self.mode == TransitionMode.FADE_IN:
            self.to_state.on_enter(game)
            self.midpoint_triggered = True

    def handle_events(self, game: "Game") -> None:
        """No input during transition."""
        pass

    def update(self, game: "Game", dt: float) -> None:
        """Update transition timer and switch when complete."""
        self.elapsed += dt

        # Trigger to_state setup based on mode (FADE_IN already handled in on_enter)
        if not self.midpoint_triggered:
            should_trigger = False

            if self.mode == TransitionMode.FADE_OUT:
                # Fade out: trigger at end (to_state shown after transition)
                should_trigger = self.elapsed >= self.TRANSITION_DURATION
            elif self.mode == TransitionMode.BOTH:
                # For both, trigger at midpoint (when fully black)
                should_trigger = self.elapsed >= self.TRANSITION_DURATION / 2

            if should_trigger:
                self.midpoint_triggered = True
                self.to_state.on_enter(game)

        # When duration complete, transition to to_state
        if self.elapsed >= self.TRANSITION_DURATION:
            game.transition_to(self.to_state)

    def draw(self, game: "Game", surface) -> None:
        """Draw transition with shrinking circle iris effect."""
        # Delegate drawing to appropriate state based on mode
        if self.mode == TransitionMode.FADE_IN:
            # Always show to_state (fading in from black)
            self.to_state.draw(game, surface)
        elif self.mode == TransitionMode.FADE_OUT:
            # Always show from_state (fading out to black)
            self.from_state.draw(game, surface)
        else:  # TransitionMode.BOTH
            # Show from_state first half, to_state second half
            if self.elapsed < self.TRANSITION_DURATION / 2:
                self.from_state.draw(game, surface)
            else:
                self.to_state.draw(game, surface)

        # Draw transition effect on top
        self._draw_transition_effect(surface)

    def _draw_transition_effect(self, surface) -> None:
        """Draw the circular iris transition effect."""
        import math

        import pygame

        from ..constants import BACKGROUND_COLOR, BLACK, NATIVE_HEIGHT, NATIVE_WIDTH

        # Calculate progress (0.0 to 1.0 over full duration)
        progress = min(1.0, self.elapsed / self.TRANSITION_DURATION)

        # Calculate radius based on transition mode
        max_radius = math.sqrt((NATIVE_WIDTH / 2) ** 2 + (NATIVE_HEIGHT / 2) ** 2)

        if self.mode == TransitionMode.FADE_OUT:
            # Fade out only: shrink from max to 0
            eased = progress * progress * (3 - 2 * progress)
            radius = max_radius * (1 - eased)
        elif self.mode == TransitionMode.FADE_IN:
            # Fade in only: expand from 0 to max
            eased = progress * progress * (3 - 2 * progress)
            radius = max_radius * eased
        else:  # TransitionMode.BOTH
            # First half: fade out (0.0 to 0.5 -> shrink from max to 0)
            # Second half: fade in (0.5 to 1.0 -> expand from 0 to max)
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
