"""Item box behavior that spawns a coin and converts to a used state."""

from __future__ import annotations

from dataclasses import dataclass

from ..constants import TILE_SIZE
from ..effects.coin import CoinEffect
from ..entities.mushroom import MushroomEntity
from .base import BehaviorContext, TerrainBehavior, TileEvent


@dataclass(slots=True)
class ItemBoxBehavior(TerrainBehavior):
    """Spawns a coin effect and turns into a used item box when hit."""

    def process(self, context: BehaviorContext) -> None:
        state = context.state
        used = state.data.get("used", False)

        if context.event == TileEvent.HIT_FROM_BELOW and not used:

            state.data["used"] = True

            coin_x = context.tile_x * TILE_SIZE
            coin_y = (context.tile_y + 1) * TILE_SIZE
            context.spawn_effect(
                CoinEffect(
                    world_x=coin_x,
                    world_y=coin_y,
                )
            )

            mushroom_x = context.tile_x * TILE_SIZE
            mushroom_y = (context.tile_y + 1) * TILE_SIZE
            context.spawn_entity(
                MushroomEntity(
                    world_x=mushroom_x,
                    world_y=mushroom_y,
                    screen=context.screen,
                    direction=1,
                )
            )

            context.queue_tile_change(
                context.screen,
                context.tile_x,
                context.tile_y,
                "item_box_used",
                behavior_type="bounce",
                behavior_params={"one_shot": True},
            )
