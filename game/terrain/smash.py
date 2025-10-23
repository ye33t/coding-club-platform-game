"""Smash behavior for breakable bricks hit from below."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..constants import TILE_SIZE
from ..content.tile_definitions import empty_tile_slug
from ..effects.score_popup import ScorePopupEffect
from ..effects.smash import SmashShardEffect
from ..physics.events import AwardScoreEvent, SpawnEffectEvent, TerrainTileChangeEvent
from .base import BehaviorContext, TerrainBehavior, TileEvent
from .bounce import BounceBehavior


@dataclass(slots=True)
class SmashBehavior(TerrainBehavior):
    """Break bricks into shards when Big Mario hits them from below."""

    bounce_behavior: BounceBehavior = field(default_factory=BounceBehavior)
    score_value: int = 50

    def process(self, context: BehaviorContext) -> None:
        """Handle smash-on-hit while preserving bounce for small Mario."""
        if context.event == TileEvent.HIT_FROM_BELOW:
            mario = context.physics.mario
            if mario.size != "small":
                self._trigger_smash(context)
                return

        self.bounce_behavior.process(context)

    def _trigger_smash(self, context: BehaviorContext) -> None:
        """Replace the tile, spawn shards, and award score."""
        state = context.state
        if state.data.get("smashed"):
            return

        state.data["smashed"] = True
        state.visual.offset_y = 0.0

        tile_world_x = context.tile_x * TILE_SIZE
        tile_world_y = context.tile_y * TILE_SIZE

        context.physics.add_event(
            SpawnEffectEvent(
                effect=SmashShardEffect(
                    tile_world_x=tile_world_x,
                    tile_world_y=tile_world_y,
                )
            )
        )
        context.physics.add_event(
            SpawnEffectEvent(
                effect=ScorePopupEffect(
                    label="50",
                    world_x=tile_world_x + TILE_SIZE / 2,
                    world_y=tile_world_y + TILE_SIZE,
                    horizontal_velocity=0.0,
                )
            )
        )
        context.physics.add_event(AwardScoreEvent(amount=self.score_value))
        context.physics.add_event(
            TerrainTileChangeEvent(
                screen=context.screen,
                x=context.tile_x,
                y=context.tile_y,
                slug=empty_tile_slug(),
                behavior_type=None,
                behavior_params=None,
            )
        )
