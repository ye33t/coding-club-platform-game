"""Bounce behavior for tiles hit from below."""

from math import pi, sin

from .base import BehaviorContext, TerrainBehavior, TileEvent

# Animation constants
BOUNCE_HEIGHT = 4.0  # pixels
BOUNCE_DURATION = 0.3  # seconds


class BounceBehavior(TerrainBehavior):
    """Makes a tile bounce when hit from below."""

    def process(self, context: BehaviorContext) -> None:
        """Process bounce animation."""
        # Start bounce on event
        if context.event == TileEvent.HIT_FROM_BELOW:
            context.state.data["bounce_timer"] = BOUNCE_DURATION

        # Animate if timer active
        timer = context.state.data.get("bounce_timer", 0.0)
        if timer > 0:
            # Sine wave animation: rises then falls
            progress = 1 - (timer / BOUNCE_DURATION)
            context.state.visual.offset_y = sin(progress * pi) * BOUNCE_HEIGHT

            timer -= context.dt
            if timer <= 0:
                # Animation complete - reset
                context.state.visual.offset_y = 0.0
                context.state.data.pop("bounce_timer", None)
            else:
                context.state.data["bounce_timer"] = timer