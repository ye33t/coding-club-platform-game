"""Main game class with NES-style game loop."""

import os
import sys

import pygame

from .constants import BACKGROUND_COLOR, FPS
from .content import sprites
from .display import Display
from .rendering import (
    DebugOverlayEffect,
    PipelineRenderer,
    TransitionCallbacks,
    TransitionEffect,
    TransitionMode,
    WorldRenderer,
)
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
        self._debug_effect: DebugOverlayEffect | None = None
        self._active_transition: TransitionEffect | None = None

        # Initialize font for debug info
        self.font = pygame.font.Font(None, 16)

        # Load sprite sheets
        assets_path = os.path.join(os.path.dirname(__file__), "assets", "images")
        sprites.load_sheets(assets_path)

        # Create World (owns level, mario, camera, physics)
        self.world = World()
        self.world_renderer = WorldRenderer(self.world)
        self.renderer = PipelineRenderer(self.world_renderer)

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

            # Handle global events
            self._handle_events()

            # Update game state
            self.state.update(self, dt)
            
            # Render frame
            self.renderer.update(dt, self)
            self.display.clear(BACKGROUND_COLOR)
            surface = self.display.get_native_surface()

            # State-specific drawing
            self.state.draw(self, surface)

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

    def render(self, surface: pygame.Surface) -> None:
        """Render the current frame via the renderer pipeline."""
        self.renderer.draw(surface, self)

    def start_transition(
        self,
        to_state: State,
        mode: TransitionMode = TransitionMode.BOTH,
        duration: float = 2.0,
    ) -> None:
        """Begin a screen transition effect while switching states."""
        if self._active_transition is not None:
            return

        def _clear(_: "Game") -> None:
            self._active_transition = None

        callbacks = TransitionCallbacks(on_complete=_clear)

        if mode == TransitionMode.FADE_OUT:

            def on_complete(game: "Game") -> None:
                self.transition_to(to_state)
                _clear(game)

            callbacks.on_complete = on_complete
        else:

            def on_midpoint(game: "Game") -> None:
                self.transition_to(to_state)

            callbacks.on_midpoint = on_midpoint

        effect = TransitionEffect(duration, mode, callbacks)
        self._active_transition = effect
        self.renderer.add_effect(effect, self)

    def _attach_debug_overlay(self) -> None:
        if self._debug_effect is None:
            self._debug_effect = DebugOverlayEffect()
            self.renderer.add_effect(self._debug_effect, self)

    def _detach_debug_overlay(self) -> None:
        if self._debug_effect is not None:
            self.renderer.remove_effect(self._debug_effect, self)
            self._debug_effect = None
            
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
                    if self.show_debug:
                        self._attach_debug_overlay()
                    else:
                        self._detach_debug_overlay()
