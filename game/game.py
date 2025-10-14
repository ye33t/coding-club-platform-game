"""Main game class with NES-style game loop."""

import os
import sys
from typing import Optional

import pygame

from .constants import FPS
from .content import sprites
from .rendering import (
    RenderPipeline,
    TransitionLayer,
    TransitionMode,
    TransitionTimeline,
)
from .states import InitialState, State
from .world import World


class Game:
    """Main game class handling the game loop and state."""

    def __init__(self) -> None:
        """Initialize pygame and game components."""
        pygame.init()

        self._renderer = RenderPipeline()
        self.clock = pygame.time.Clock()
        self.running = True

        assets_path = os.path.join(os.path.dirname(__file__), "assets", "images")
        sprites.load_sheets(assets_path)

        self.world = World()
        self.state: State = InitialState()
        self.state.on_enter(self)
        self.dt: float = 0
        self._pending_state: Optional[State] = None
        self._transition_timeline: Optional[TransitionTimeline] = None

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
            self.dt = self.clock.tick(FPS) / 1000.0

            # Handle global events
            self._handle_events()

            # Update game state
            self.state.update(self, self.dt)

            # Render frame
            self._renderer.draw(self)

            # Update transition timeline
            self._tick_transition()

        # Cleanup
        pygame.quit()
        sys.exit()

    def transition(
        self,
        to_state: State,
        mode: TransitionMode = TransitionMode.INSTANT,
    ) -> None:
        """Transition to a new state using the requested mode."""

        timeline = TransitionTimeline(mode)
        self._transition_timeline = timeline
        self._pending_state = to_state
        self._renderer.enqueue_effect(TransitionLayer(timeline))

    def _apply_state_change(self, new_state: State) -> None:
        """Switch to a new game state immediately."""
        self.state.on_exit(self)
        self.state = new_state
        self.state.on_enter(self)

    def _tick_transition(self) -> None:
        if self._transition_timeline is None:
            return

        timeline = self._transition_timeline
        if self._pending_state and timeline.ready_for_state_swap():
            self._apply_state_change(self._pending_state)
            self._pending_state = None
            timeline.mark_state_swapped()

        if timeline.is_complete:
            self._transition_timeline = None
            self._pending_state = None

    def _handle_events(self) -> None:
        """Handle global events (ESC, scaling, debug toggle)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from .states.start_level import StartLevelState

                    self.transition(StartLevelState())
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self._renderer.change_scale(-1)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    self._renderer.change_scale(1)
                elif event.key == pygame.K_F3:
                    self._renderer.toggle_debug()
