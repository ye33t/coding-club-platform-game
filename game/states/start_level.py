"""Start level state - positions Mario and initializes level."""

from .base import State


class StartLevelState(State):
    """State for starting or restarting a level.

    This state:
    - Positions Mario at the level's spawn point
    - Resets camera to origin
    - Immediately transitions to PlayingState
    """

    def on_enter(self, game) -> None:
        """Initialize level start."""
        # Reset Mario to spawn point
        game.world.mario.reset(
            x=game.world.level.spawn_x,
            y=game.world.level.spawn_y,
            screen=game.world.level.spawn_screen,
        )

        # Reset terrain and clear active effects and entities
        game.world.level.reset_terrain()
        game.world.effects.clear()
        game.world.entities.clear()

        # Reset spawn triggers for the level
        game.world.reset_spawn_triggers()

        # Reset camera to beginning (both position and ratchet)
        game.world.camera.x = 0
        game.world.camera.max_x = 0

    def handle_events(self, game) -> None:
        """No events during instant transition."""
        pass

    def update(self, game, dt: float) -> None:
        # Immediately transition to playing
        from .playing import PlayingState

        game.transition_to(PlayingState())

    def draw(self, game, surface) -> None:
        """Draw the initial state."""
        game.draw_world(surface)
