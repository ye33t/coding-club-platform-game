"""Main game class with NES-style game loop."""

import os
import sys

import pygame

from .constants import FPS
from .content import sprites
from .rendering import RenderPipeline, TransitionLayer, TransitionMode
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

        # Cleanup
        pygame.quit()
        sys.exit()

    def transition(
        self,
        to_state: State,
        mode: TransitionMode = TransitionMode.INSTANT,
    ) -> None:
        """Transition to a new state using the requested mode."""

        def apply_to_state() -> None:
            print(f"Transitioning to {to_state.__class__.__name__} with mode {mode}")
            self._apply_state_change(to_state)
            
        if mode == TransitionMode.INSTANT:
            apply_to_state()
            return

        self._renderer.set_effect(TransitionLayer(
            mode,
            on_transition=lambda: apply_to_state(),
        ))

    def _apply_state_change(self, new_state: State) -> None:
        """Switch to a new game state immediately."""
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

                    self.transition(StartLevelState())
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self._renderer.change_scale(-1)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    self._renderer.change_scale(1)
                elif event.key == pygame.K_F3:
                    self._renderer.toggle_debug()
