"""Bounce behavior for tiles hit from below."""

from dataclasses import dataclass

from ..physics.config import BOUNCE_DURATION, BOUNCE_GRAVITY, BOUNCE_VELOCITY
from .base import BehaviorContext, TerrainBehavior, TileEvent


@dataclass(slots=True)
class BounceBehavior(TerrainBehavior):
    """Makes a tile bounce when hit from below with physics-based motion.

    Args:
        one_shot: If True, starts bouncing immediately on creation and only
                  bounces once. If False, bounces every time HIT_FROM_BELOW
                  event is triggered.
    """

    one_shot: bool = False

    def process(self, context: BehaviorContext) -> None:
        """Process bounce animation using physics."""
        # For one-shot, start bouncing immediately on first process call
        if self.one_shot and "one_shot_started" not in context.state.data:
            context.state.data["bounce_timer"] = BOUNCE_DURATION
            context.state.data["one_shot_started"] = True
        # For regular bounce, respond to HIT_FROM_BELOW events
        elif not self.one_shot and context.event == TileEvent.HIT_FROM_BELOW:
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
