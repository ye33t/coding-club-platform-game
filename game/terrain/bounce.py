"""Bounce behavior for tiles hit from below."""

from ..physics.config import BOUNCE_DURATION, BOUNCE_GRAVITY, BOUNCE_VELOCITY
from .base import BehaviorContext, TerrainBehavior, TileEvent


class BounceBehavior(TerrainBehavior):
    """Makes a tile bounce when hit from below with physics-based motion."""

    def process(self, context: BehaviorContext) -> None:
        """Process bounce animation using physics."""
        # Start bounce on event
        if context.event == TileEvent.HIT_FROM_BELOW:
            context.state.data["bounce_timer"] = BOUNCE_DURATION

        # Animate if timer active
        timer = context.state.data.get("bounce_timer", 0.0)
        if timer > 0:
            # Physics-based animation: y = v*t - 0.5*g*t^2
            elapsed = BOUNCE_DURATION - timer
            offset = (BOUNCE_VELOCITY * elapsed) - (
                0.5 * BOUNCE_GRAVITY * elapsed * elapsed
            )

            # Clamp to not go below starting position
            context.state.visual.offset_y = max(0, offset)

            timer -= context.dt
            if timer <= 0:
                # Animation complete - reset
                context.state.visual.offset_y = 0.0
                context.state.data.pop("bounce_timer", None)
            else:
                context.state.data["bounce_timer"] = timer
