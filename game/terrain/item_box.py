"""Item box behavior that spawns a coin and converts to a used state."""

from __future__ import annotations

from dataclasses import dataclass

from ..constants import TILE_SIZE
from ..effects.coin import CoinEffect
from .base import BehaviorContext, TerrainBehavior, TileEvent
from .bounce import BounceBehavior


@dataclass(slots=True)
class ItemBoxBehavior(BounceBehavior):
    """Spawns a coin effect and turns into a used item box when hit."""

    used_slug: str = "item_box_used"
    coin_sheet: str = "background"
    coin_sprite: str = "coin"


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
                    on_collect=None,
                    sprite_sheet=self.coin_sheet,
                    sprite_name=self.coin_sprite,
                )
            )

        # Call BounceBehavior directly to avoid super() issues when hot-reloading
        BounceBehavior.process(self, context)
        
    def on_complete(self, context: BehaviorContext) -> None:
        """Handle completion of bounce animation."""
        context.queue_tile_change(
                context.screen, context.tile_x, context.tile_y, self.used_slug
            )
